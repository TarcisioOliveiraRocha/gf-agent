from __future__ import annotations

import base64
import io
import os
import glob
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pypdf import PdfReader


@dataclass(frozen=True)
class PdfExtractResult:
    text: str
    pages: int
    method: str  # "text", "ocr" ou "vision"


# Threshold mínimo de caracteres para considerar que o OCR funcionou bem
_OCR_MIN_CHARS = 100


class PdfTextExtractor:
    def extract(self, file_bytes: bytes, *, max_pages: Optional[int] = None) -> PdfExtractResult:
        # 1) Tenta extrair texto normal (PDF com texto selecionável)
        reader = PdfReader(io.BytesIO(file_bytes), strict=False)
        total_pages = len(reader.pages)
        pages_to_read = total_pages if max_pages is None else min(total_pages, max_pages)

        parts: list[str] = []
        for i in range(pages_to_read):
            page_text = (reader.pages[i].extract_text() or "").strip()
            if page_text:
                parts.append(f"\n--- Página {i+1} ---\n{page_text}")

        text = "\n".join(parts).strip()

        if text:
            return PdfExtractResult(text=text, pages=total_pages, method="text")

        # 2) PDF sem texto → tenta OCR
        return self._extract_with_ocr(file_bytes, pages_to_read, total_pages)

    # ------------------------------------------------------------------
    # OCR via Tesseract + Poppler
    # ------------------------------------------------------------------
    def _extract_with_ocr(
        self,
        file_bytes: bytes,
        pages_to_read: int,
        total_pages: int,
    ) -> PdfExtractResult:
        import pytesseract
        from PIL import Image

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        poppler_path = os.environ.get("POPPLER_PATH") or r"C:\poppler\poppler-25.12.0\Library\bin"
        pdftoppm = str(Path(poppler_path) / "pdftoppm.exe")

        base_tmp = Path(r"C:\Temp\pdf_ocr_tmp")
        base_tmp.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(dir=base_tmp) as tmpdir:
            tmpdir_path = Path(tmpdir)
            pdf_path = tmpdir_path / "input.pdf"
            pdf_path.write_bytes(file_bytes)
            out_prefix = tmpdir_path / "pg"

            cmd = [
                pdftoppm,
                "-f", "1",
                "-l", str(pages_to_read),
                "-png",
                "-r", "200",
                str(pdf_path),
                str(out_prefix),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "Falha ao converter PDF para imagem via pdftoppm.\n"
                    f"Comando: {' '.join(cmd)}\n"
                    f"STDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"
                )

            png_files = sorted(
                glob.glob(str(tmpdir_path / "pg-*.png")),
                key=lambda p: int(Path(p).stem.split("-")[-1]),
            )

            if not png_files:
                raise RuntimeError(
                    "pdftoppm executou sem erros mas não gerou nenhuma imagem PNG.\n"
                    f"Arquivos presentes: {list(tmpdir_path.iterdir())}"
                )

            ocr_parts: list[str] = []
            png_bytes_list: list[tuple[int, bytes]] = []

            for idx, png in enumerate(png_files, start=1):
                img = Image.open(png)
                img_gray = img.convert("L")

                try:
                    page_txt = pytesseract.image_to_string(
                        img_gray, lang="por+eng", config="--psm 3"
                    ).strip()
                except Exception:
                    page_txt = pytesseract.image_to_string(
                        img_gray, lang="eng", config="--psm 3"
                    ).strip()

                if page_txt:
                    ocr_parts.append(f"\n--- Página {idx} (OCR) ---\n{page_txt}")

                # Guarda bytes PNG para eventual uso no Vision
                png_bytes_list.append((idx, Path(png).read_bytes()))

            ocr_text = "\n".join(ocr_parts).strip()

        # 3) OCR retornou pouco texto → provavelmente diagrama → Claude Vision
        if len(ocr_text) < _OCR_MIN_CHARS:
            return self._extract_with_vision(png_bytes_list, total_pages)

        return PdfExtractResult(text=ocr_text, pages=total_pages, method="ocr")

    # ------------------------------------------------------------------
    # Claude Vision — para diagramas e imagens complexas
    # ------------------------------------------------------------------
    def _extract_with_vision(
        self,
        png_bytes_list: list[tuple[int, bytes]],
        total_pages: int,
    ) -> PdfExtractResult:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OCR retornou resultado insuficiente e ANTHROPIC_API_KEY não está definida. "
                "Configure a variável de ambiente para habilitar análise de diagramas via Claude Vision."
            )

        client = anthropic.Anthropic(api_key=api_key)

        vision_parts: list[str] = []

        for idx, png_bytes in png_bytes_list:
            b64 = base64.standard_b64encode(png_bytes).decode("utf-8")

            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Analise esta imagem extraída de um PDF. "
                                    "Ela pode ser um documento, diagrama, fluxograma ou tabela. "
                                    "Por favor:\n"
                                    "1. Descreva o conteúdo geral da imagem\n"
                                    "2. Extraia TODO o texto visível, mantendo a estrutura lógica\n"
                                    "3. Se for um fluxograma/diagrama, explique o fluxo ou a lógica representada\n"
                                    "Responda em português."
                                ),
                            },
                        ],
                    }
                ],
            )

            response_text = message.content[0].text.strip()
            vision_parts.append(f"\n--- Página {idx} (Vision) ---\n{response_text}")

        vision_text = "\n".join(vision_parts).strip()
        return PdfExtractResult(text=vision_text, pages=total_pages, method="vision")