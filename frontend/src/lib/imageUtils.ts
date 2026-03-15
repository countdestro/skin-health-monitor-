const MAX_DIM = 800;
const JPEG_QUALITY = 0.85;

export function compressImageToBase64(
  dataUrl: string,
  maxDim: number = MAX_DIM,
  quality: number = JPEG_QUALITY
): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = document.createElement("img");
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const canvas = document.createElement("canvas");
      let { width, height } = img;
      if (width > maxDim || height > maxDim) {
        if (width >= height) {
          height = Math.round((height * maxDim) / width);
          width = maxDim;
        } else {
          width = Math.round((width * maxDim) / height);
          height = maxDim;
        }
      }
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        reject(new Error("Canvas not supported"));
        return;
      }
      ctx.drawImage(img, 0, 0, width, height);
      const out = canvas.toDataURL("image/jpeg", quality);
      resolve(out.split(",")[1] ?? "");
    };
    img.onerror = () => reject(new Error("Failed to load image"));
    img.src = dataUrl;
  });
}

export function dataUrlToBase64(dataUrl: string): string {
  const base64 = dataUrl.split(",")[1];
  if (!base64) throw new Error("Invalid data URL");
  return base64;
}
