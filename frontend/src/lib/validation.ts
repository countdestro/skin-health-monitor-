const ALLOWED_MIMES = ["image/jpeg", "image/png", "image/webp"];
const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
const MIN_SIDE_PX = 224;

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

export function validateMimeType(mime: string): ValidationResult {
  if (!ALLOWED_MIMES.includes(mime)) {
    return {
      valid: false,
      error: "Please use a JPEG, PNG or WebP image.",
    };
  }
  return { valid: true };
}

export function validateFileSize(bytes: number): ValidationResult {
  if (bytes > MAX_SIZE_BYTES) {
    return {
      valid: false,
      error: "Image must be 10 MB or smaller.",
    };
  }
  return { valid: true };
}

export function validateResolution(width: number, height: number): ValidationResult {
  if (width < MIN_SIDE_PX || height < MIN_SIDE_PX) {
    return {
      valid: false,
      error: "Image too small — please use a photo at least 224×224 px (e.g. taken in good lighting).",
    };
  }
  return { valid: true };
}

export async function getImageDimensions(
  file: File
): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const img = document.createElement("img");
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve({ width: img.naturalWidth, height: img.naturalHeight });
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Failed to load image"));
    };
    img.src = url;
  });
}

export async function validateImageFile(file: File): Promise<ValidationResult> {
  const mime = validateMimeType(file.type);
  if (!mime.valid) return mime;
  const size = validateFileSize(file.size);
  if (!size.valid) return size;
  try {
    const { width, height } = await getImageDimensions(file);
    return validateResolution(width, height);
  } catch {
    return { valid: false, error: "Could not read image dimensions." };
  }
}

export function validateDataUrlDimensions(
  dataUrl: string
): Promise<ValidationResult> {
  return new Promise((resolve) => {
    const img = document.createElement("img");
    img.onload = () => {
      resolve(
        validateResolution(img.naturalWidth, img.naturalHeight)
      );
    };
    img.onerror = () => resolve({ valid: false, error: "Invalid image." });
    img.src = dataUrl;
  });
}
