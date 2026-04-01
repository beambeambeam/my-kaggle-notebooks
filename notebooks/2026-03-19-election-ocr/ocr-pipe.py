import gc
import glob
import os
import re
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import pandas as pd
import torch
from PIL import Image
from tqdm.auto import tqdm
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from olmocr.prompts import build_no_anchoring_v4_yaml_prompt


IMAGE_PATH = "./constituency_10_1.png"
ZIP_PATH = "./super-ai-engineer-season-6-ocr-2569.zip"
EXTRACT_DIR = "./data"
IMAGE_DIR = "./data/data/images"
LABEL_DIR = "./data/data/sample_labels"
SUBMISSION_TEMPLATE = "./data/data/submission_template.csv"
OUTPUT_CSV = "ocr_documents.csv"

MAX_BATCH_SIZE = 16
MIN_BATCH_SIZE = 1
FLUSH_EVERY_N_DOCS = 25
MAX_IMAGE_SIZE = (1600, 1600)
MAX_NEW_TOKENS = 4096
GMT_PLUS_7 = timezone(timedelta(hours=7))

PAGE_RE = re.compile(
    r"^(?P<doc_id>(?P<doc_type>constituency|party_list)_(?P<province_code>\d+)_(?P<constituency>\d+))(?:_page(?P<page>\d+))?\.png$",
    re.IGNORECASE,
)


def clear_gpu_memory() -> None:
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    log("GPU memory cleared")


def now_gmt_plus_7() -> str:
    return datetime.now(GMT_PLUS_7).strftime("%Y-%m-%d %H:%M:%S GMT+7")


def log(message: str) -> None:
    print(f"[{now_gmt_plus_7()}] {message}")


def log_section(title: str) -> None:
    log(f"===== {title} =====")


def load_model():
    log_section("MODEL LOAD START")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_kwargs = {
        "torch_dtype": torch.bfloat16 if device.type == "cuda" else torch.float32,
    }

    if device.type == "cuda":
        model_kwargs["attn_implementation"] = "flash_attention_2"

    try:
        model = (
            Qwen2_5_VLForConditionalGeneration.from_pretrained(
                "allenai/olmOCR-2-7B-1025",
                **model_kwargs,
            )
            .eval()
            .to(device)
        )
    except Exception as exc:
        if model_kwargs.get("attn_implementation") != "flash_attention_2":
            raise
        log(f"flash_attention_2 unavailable, falling back to default attention: {exc}")
        model_kwargs.pop("attn_implementation", None)
        model = (
            Qwen2_5_VLForConditionalGeneration.from_pretrained(
                "allenai/olmOCR-2-7B-1025",
                **model_kwargs,
            )
            .eval()
            .to(device)
        )

    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")

    log("Model loaded")
    log(f"Device: {device}")
    log(f"Model kwargs: {model_kwargs}")
    log_section("MODEL LOAD DONE")
    return device, model, processor


def prepare_image(image_path: str, max_image_size=MAX_IMAGE_SIZE) -> Image.Image:
    img = Image.open(image_path).convert("RGB")
    original_size = img.size
    img.thumbnail(max_image_size)
    log(f"Prepared image {image_path} from {original_size} to {img.size}")
    return img


def build_message():
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": build_no_anchoring_v4_yaml_prompt()},
                {"type": "image"},
            ],
        }
    ]


def is_oom_error(exc: RuntimeError) -> bool:
    message = str(exc).lower()
    return "out of memory" in message or "cuda error: out of memory" in message


def run_ocr_batch(image_paths, device, model, processor, batch_size=MAX_BATCH_SIZE):
    if not image_paths:
        log("run_ocr_batch received no images")
        return []

    log_section("OCR BATCH START")
    log(f"Incoming images: {len(image_paths)}")
    log(f"Requested batch size: {batch_size}")
    prompt_messages = build_message()
    all_outputs = []
    index = 0
    current_batch_size = min(batch_size, len(image_paths))

    while index < len(image_paths):
        current_batch_size = max(MIN_BATCH_SIZE, min(current_batch_size, len(image_paths) - index))
        batch_paths = image_paths[index : index + current_batch_size]
        batch_start = datetime.now(GMT_PLUS_7)
        log(
            f"Starting sub-batch at index {index} with size {current_batch_size}: {batch_paths}"
        )
        images = [prepare_image(path) for path in batch_paths]
        texts = [
            processor.apply_chat_template(
                prompt_messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            for _ in images
        ]

        try:
            inputs = processor(
                text=texts,
                images=images,
                padding=True,
                return_tensors="pt",
            )
            inputs = {key: value.to(device) for key, value in inputs.items()}
            log(
                "Processor output shapes: "
                + ", ".join(f"{key}={tuple(value.shape)}" for key, value in inputs.items())
            )

            with torch.inference_mode():
                output = model.generate(
                    **inputs,
                    temperature=0,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False,
                )

            prompt_lengths = inputs["attention_mask"].sum(dim=1).tolist()
            new_tokens = [
                output[row_index, prompt_length:]
                for row_index, prompt_length in enumerate(prompt_lengths)
            ]
            decoded = processor.tokenizer.batch_decode(
                new_tokens,
                skip_special_tokens=True,
            )
            all_outputs.extend(text.strip() for text in decoded)
            batch_duration = (datetime.now(GMT_PLUS_7) - batch_start).total_seconds()
            log(
                f"Completed sub-batch size {current_batch_size} in {batch_duration:.2f}s; "
                f"decoded {len(decoded)} page(s)"
            )
            index += current_batch_size
        except RuntimeError as exc:
            if device.type != "cuda" or not is_oom_error(exc):
                log(f"Runtime error during OCR batch: {exc}")
                raise
            if current_batch_size == MIN_BATCH_SIZE:
                log("OOM happened at minimum batch size; re-raising")
                raise
            clear_gpu_memory()
            next_batch_size = max(MIN_BATCH_SIZE, current_batch_size // 2)
            log(
                f"CUDA OOM at batch size {current_batch_size}; retrying with batch size {next_batch_size}"
            )
            current_batch_size = next_batch_size
        finally:
            for image in images:
                image.close()

    log(f"OCR batch complete with {len(all_outputs)} outputs")
    log_section("OCR BATCH DONE")
    return all_outputs


def run_ocr_single_image(image_path: str, device, model, processor) -> str:
    log_section("SINGLE IMAGE OCR START")
    log(f"Single image path: {image_path}")
    result = run_ocr_batch([image_path], device, model, processor, batch_size=1)[0]
    log(f"Single image OCR output length: {len(result)}")
    log_section("SINGLE IMAGE OCR DONE")
    return result


def unzip_dataset(zip_path: str = ZIP_PATH, extract_dir: str = EXTRACT_DIR) -> None:
    log_section("UNZIP START")
    log(f"Zip path: {zip_path}")
    log(f"Extract dir: {extract_dir}")
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    log("Unzip complete")
    log(f"Extracted to: {extract_dir}")
    log(f"Top-level extracted entries: {os.listdir(extract_dir)}")
    log_section("UNZIP DONE")


def inspect_tree(base: str = EXTRACT_DIR) -> None:
    log_section("TREE INSPECTION START")
    for root, dirs, files in os.walk(base):
        log(root)
        for directory in dirs:
            log(f"  [DIR] {directory}")
        for filename in files[:5]:
            log(f"  [FILE] {filename}")
    log_section("TREE INSPECTION DONE")


def print_dataset_summary() -> None:
    log_section("DATASET SUMMARY")
    log(f"Images: {len(os.listdir(IMAGE_DIR))}")
    log(f"Labels: {len(os.listdir(LABEL_DIR))}")
    log(f"Template exists: {os.path.exists(SUBMISSION_TEMPLATE)}")


def parse_filename(filepath: str):
    name = os.path.basename(filepath)
    match = PAGE_RE.match(name)

    if not match:
        return None

    return {
        "filepath": filepath,
        "filename": name,
        "doc_id": match.group("doc_id"),
        "doc_type": match.group("doc_type"),
        "province_code": match.group("province_code"),
        "constituency": match.group("constituency"),
        "page": int(match.group("page")) if match.group("page") else 1,
    }


def group_document_pages(image_dir: str = IMAGE_DIR):
    log_section("GROUP DOCUMENTS START")
    log(f"Image dir: {image_dir}")
    all_pngs = glob.glob(f"{image_dir}/*.png")
    grouped_docs = {}

    for path in all_pngs:
        info = parse_filename(path)

        if info is None:
            log(f"Skipping unmatched filename: {path}")
            continue

        grouped_docs.setdefault(info["doc_id"], []).append(info)

    for doc_id in grouped_docs:
        grouped_docs[doc_id] = sorted(grouped_docs[doc_id], key=lambda item: item["page"])

    log(f"Total PNG: {len(all_pngs)}")
    log(f"Total documents: {len(grouped_docs)}")
    log_section("GROUP DOCUMENTS DONE")
    return grouped_docs


def print_example_document(grouped_docs) -> None:
    example_doc = sorted(grouped_docs.keys())[0]
    log_section("EXAMPLE DOCUMENT")
    log(f"Example doc: {example_doc}")

    for page in grouped_docs[example_doc]:
        log(f"Page {page['page']}: {page['filename']}")


def load_processed_ids(output_csv: str = OUTPUT_CSV):
    if not os.path.exists(output_csv):
        log(f"Output CSV does not exist yet: {output_csv}")
        return set()

    df = pd.read_csv(output_csv)
    if "id" not in df.columns:
        log(f"Output CSV missing 'id' column: {output_csv}")
        return set()
    processed_ids = set(df["id"].astype(str).tolist())
    log(f"Loaded {len(processed_ids)} processed ids from {output_csv}")
    return processed_ids


def append_rows(rows, output_csv: str = OUTPUT_CSV) -> None:
    if not rows:
        log("append_rows called with no rows")
        return

    file_exists = os.path.exists(output_csv)
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, mode="a", header=not file_exists, index=False)
    log(f"Appended {len(rows)} rows to {output_csv}")


def build_doc_batches(grouped_docs, pending_doc_ids, max_batch_size=MAX_BATCH_SIZE):
    log_section("BUILD DOC BATCHES START")
    log(f"Pending doc ids: {len(pending_doc_ids)}")
    log(f"Max batch size: {max_batch_size}")
    batches = []
    current_batch = []
    current_pages = 0

    for doc_id in pending_doc_ids:
        doc_pages = grouped_docs[doc_id]
        page_count = len(doc_pages)

        if current_batch and current_pages + page_count > max_batch_size:
            batches.append(current_batch)
            current_batch = []
            current_pages = 0

        current_batch.append((doc_id, doc_pages))
        current_pages += page_count

        if current_pages >= max_batch_size:
            batches.append(current_batch)
            current_batch = []
            current_pages = 0

    if current_batch:
        batches.append(current_batch)

    log(f"Built {len(batches)} document batch(es)")
    log_section("BUILD DOC BATCHES DONE")
    return batches


def run_batch_ocr(grouped_docs, device, model, processor, output_csv: str = OUTPUT_CSV) -> None:
    log_section("RUN BATCH OCR START")
    processed_ids = load_processed_ids(output_csv)
    pending_doc_ids = [
        doc_id for doc_id in sorted(grouped_docs.keys()) if doc_id not in processed_ids
    ]

    log(f"Already processed: {len(processed_ids)}")
    log(f"Pending documents: {len(pending_doc_ids)}")

    if not pending_doc_ids:
        log("No pending documents; exiting batch OCR")
        log_section("RUN BATCH OCR DONE")
        return

    pending_rows = []
    docs_since_flush = 0
    doc_batches = build_doc_batches(grouped_docs, pending_doc_ids)
    total_docs = len(pending_doc_ids)
    completed_docs = 0

    for batch_index, batch in enumerate(
        tqdm(
            doc_batches,
            desc="OCR document batches",
        ),
        start=1,
    ):
        log_section(f"DOCUMENT BATCH {batch_index}/{len(doc_batches)} START")
        log(
            "Documents in batch: "
            + ", ".join(f"{doc_id}({len(doc_pages)} pages)" for doc_id, doc_pages in batch)
        )
        batch_started_at = datetime.now(GMT_PLUS_7)
        for doc_id, doc_pages in batch:
            log(f"Queueing document {doc_id} with {len(doc_pages)} page(s)")

        batch_page_paths = []
        batch_page_map = []

        for doc_id, doc_pages in batch:
            for page in doc_pages:
                batch_page_paths.append(page["filepath"])
                batch_page_map.append((doc_id, page["page"]))

        log(f"Total page paths in this document batch: {len(batch_page_paths)}")
        page_texts = run_ocr_batch(
            batch_page_paths,
            device,
            model,
            processor,
            batch_size=MAX_BATCH_SIZE,
        )

        doc_texts = defaultdict(list)
        for (doc_id, page_number), text in zip(batch_page_map, page_texts):
            log(
                f"OCR result ready for {doc_id} page {page_number} with text length {len(text)}"
            )
            doc_texts[doc_id].append(text)

        for doc_id, doc_pages in batch:
            combined_text = "\n\n".join(doc_texts[doc_id])
            pending_rows.append({"id": doc_id, "text": combined_text})
            processed_ids.add(doc_id)
            docs_since_flush += 1
            completed_docs += 1
            log(
                f"Prepared document {doc_id} with {len(doc_pages)} page(s), "
                f"combined text length {len(combined_text)} "
                f"({completed_docs}/{total_docs})"
            )

        if docs_since_flush >= FLUSH_EVERY_N_DOCS:
            append_rows(pending_rows, output_csv)
            log(f"Flush threshold reached at {docs_since_flush} document(s)")
            pending_rows = []
            docs_since_flush = 0

        batch_duration = (datetime.now(GMT_PLUS_7) - batch_started_at).total_seconds()
        log(f"Document batch {batch_index} finished in {batch_duration:.2f}s")
        log_section(f"DOCUMENT BATCH {batch_index}/{len(doc_batches)} DONE")

    append_rows(pending_rows, output_csv)
    if pending_rows:
        log(f"Final flush wrote {len(pending_rows)} document(s)")

    log_section("RUN BATCH OCR DONE")


def main() -> None:
    log_section("PROGRAM START")
    clear_gpu_memory()
    device, model, processor = load_model()

    if os.path.exists(IMAGE_PATH):
        log(f"Sample image found: {IMAGE_PATH}")
        sample_text = run_ocr_single_image(IMAGE_PATH, device, model, processor)
        log(f"Sample OCR preview length: {len(sample_text)}")
        print(sample_text)
    else:
        log(f"Sample image not found: {IMAGE_PATH}")

    if os.path.exists(ZIP_PATH):
        log(f"Dataset zip found: {ZIP_PATH}")
        unzip_dataset()
        inspect_tree()
        print_dataset_summary()

        grouped_docs = group_document_pages()
        if grouped_docs:
            print_example_document(grouped_docs)
            run_batch_ocr(grouped_docs, device, model, processor)
        else:
            log("No grouped documents found after scanning image directory")
    else:
        log(f"Dataset zip not found: {ZIP_PATH}")

    log_section("PROGRAM DONE")


if __name__ == "__main__":
    main()
