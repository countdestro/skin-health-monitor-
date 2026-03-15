"use client";

import { useCallback, useRef, useState } from "react";
import Webcam from "react-webcam";
import { Camera, Upload } from "lucide-react";
import {
  validateImageFile,
  validateDataUrlDimensions,
  type ValidationResult,
} from "@/lib/validation";
import { useSessionStore } from "@/store/sessionStore";
import { LoadingScreen } from "./LoadingScreen";
import { RippleButton } from "./RippleButton";

const videoConstraints = {
  facingMode: "user" as const,
  width: 640,
  height: 480,
};

type Tab = "camera" | "upload";

interface CaptureScreenProps {
  onError: (message: string) => void;
}

export function CaptureScreen({ onError }: CaptureScreenProps) {
  const [tab, setTab] = useState<Tab>("camera");
  const [capturedDataUrl, setCapturedDataUrl] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingPhase, setLoadingPhase] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const getOrCreateSessionId = useSessionStore((s) => s.getOrCreateSessionId());

  const handleValidation = useCallback((result: ValidationResult) => {
    if (!result.valid) {
      setValidationError(result.error ?? "Validation failed");
      return;
    }
    setValidationError(null);
  }, []);

  const handleCapture = useCallback(() => {
    const src = webcamRef.current?.getScreenshot();
    if (!src) {
      onError("Could not capture from camera.");
      return;
    }
    setCapturedDataUrl(src);
    validateDataUrlDimensions(src).then(handleValidation);
  }, [handleValidation, onError]);

  const handleFileSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const result = await validateImageFile(file);
      if (!result.valid) {
        setValidationError(result.error ?? "Validation failed");
        return;
      }
      setValidationError(null);
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = reader.result as string;
        setCapturedDataUrl(dataUrl);
        validateDataUrlDimensions(dataUrl).then(handleValidation);
      };
      reader.readAsDataURL(file);
      e.target.value = "";
    },
    [handleValidation]
  );

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (!file) return;
      if (!file.type.startsWith("image/")) {
        setValidationError("Please use a JPEG, PNG or WebP image.");
        return;
      }
      const result = await validateImageFile(file);
      if (!result.valid) {
        setValidationError(result.error ?? "Validation failed");
        return;
      }
      setValidationError(null);
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = reader.result as string;
        setCapturedDataUrl(dataUrl);
        validateDataUrlDimensions(dataUrl).then(handleValidation);
      };
      reader.readAsDataURL(file);
    },
    [handleValidation]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleAnalyse = useCallback(
    async (imageDataUrl: string) => {
      setIsLoading(true);
      setLoadingPhase(0);
      const phases = [
        "Detecting face…",
        "Analysing skin…",
        "Generating insights…",
      ];
      const phaseInterval = setInterval(() => {
        setLoadingPhase((p) => Math.min(p + 1, phases.length - 1));
      }, 2500);
      try {
        const { compressImageToBase64 } = await import("@/lib/imageUtils");
        const base64 = await compressImageToBase64(imageDataUrl);
        const sessionId = getOrCreateSessionId();
        const { analyseImage } = await import("@/lib/api");
        const envelope = await analyseImage(base64, sessionId);
        clearInterval(phaseInterval);
        if (envelope.success && envelope.data) {
          window.location.href = `/results/${envelope.data.analysis_id}`;
          return;
        }
        if (envelope.code === "NO_FACE_DETECTED") {
          onError(
            "No face detected. Please ensure your face is centred, well lit, and unobstructed, then try again."
          );
          return;
        }
        if (envelope.code === "TIMEOUT") {
          onError(
            "Request took too long. Check your connection and try again, or use a smaller image."
          );
          return;
        }
        if (envelope.code === "RATE_LIMIT_EXCEEDED") {
          onError("Too many requests. Please wait a minute and try again.");
          return;
        }
        if (envelope.code === "INVALID_IMAGE" || envelope.code === "LOW_QUALITY_IMAGE") {
          onError(envelope.message || "Image was rejected. Try another photo.");
          return;
        }
        onError(
          envelope.message ||
            "Something went wrong. Please try again or contact support."
        );
      } catch (err) {
        clearInterval(phaseInterval);
        onError((err as Error).message || "An error occurred.");
      } finally {
        setIsLoading(false);
      }
    },
    [getOrCreateSessionId, onError]
  );

  if (isLoading) {
    return (
      <LoadingScreen
        messages={["Detecting face…", "Analysing skin…", "Generating insights…"]}
        currentPhase={loadingPhase}
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* Pill toggle with sliding indicator */}
      <div className="relative flex rounded-full bg-zinc-200/80 p-1">
        <div
          className="absolute top-1 left-1 h-[calc(100%-8px)] w-[calc(50%-4px)] rounded-full bg-white shadow-card transition-all duration-250 ease-smooth"
          style={{ transform: tab === "upload" ? "translateX(100%)" : "translateX(0)" }}
        />
        <button
          type="button"
          onClick={() => setTab("camera")}
          className={`relative z-10 flex flex-1 items-center justify-center rounded-full py-2.5 text-sm font-medium transition-colors duration-250 ${
            tab === "camera" ? "text-zinc-900" : "text-zinc-500"
          }`}
        >
          Live camera
        </button>
        <button
          type="button"
          onClick={() => setTab("upload")}
          className={`relative z-10 flex flex-1 items-center justify-center rounded-full py-2.5 text-sm font-medium transition-colors duration-250 ${
            tab === "upload" ? "text-zinc-900" : "text-zinc-500"
          }`}
        >
          Upload photo
        </button>
      </div>

      {validationError && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50/90 p-4 text-sm text-amber-800">
          {validationError}
        </div>
      )}

      {cameraError && tab === "camera" && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50/90 p-4 text-sm text-amber-800">
          {cameraError} Use the Upload tab if you prefer to use a photo file.
        </div>
      )}

      {tab === "camera" && (
        <div
          className="overflow-hidden rounded-2xl border-[1.5px] border-teal/40 bg-white shadow-soft"
          style={{ boxShadow: "0 0 0 1px rgba(0,184,148,0.08), 0 2px 15px -3px rgba(0,0,0,0.06)" }}
        >
          <div className="relative aspect-[4/3] overflow-hidden bg-zinc-900">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              onUserMedia={() => setCameraReady(true)}
              onUserMediaError={() => {
                setCameraReady(false);
                setCameraError(
                  "Camera access denied. Enable the camera in your browser or device settings."
                );
              }}
              className="absolute inset-0 h-full w-full object-cover"
            />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div
                className={`h-52 w-40 rounded-full border-2 border-dashed border-teal/70 bg-teal/5 ${
                  cameraReady ? "animate-pulse-oval" : ""
                }`}
                style={{
                  boxShadow: "inset 0 0 30px rgba(0,184,148,0.15)",
                }}
              />
              {capturedDataUrl && (
                <span className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-teal/90 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm">
                  Face detected ✓
                </span>
              )}
            </div>
          </div>
          <div className="p-4">
            <RippleButton
              onClick={handleCapture}
              className="group relative w-full overflow-hidden rounded-[14px] bg-gradient-to-r from-[#00B894] to-[#00897B] px-4 py-3.5 font-bold text-white shadow-soft transition-all duration-250 ease-smooth hover:-translate-y-0.5 hover:shadow-card-hover"
            >
              <span className="absolute inset-0 opacity-0 transition-opacity group-hover:opacity-100 group-hover:animate-shimmer shimmer-sweep" />
              <Camera className="h-5 w-5 shrink-0" />
              Capture
            </RippleButton>
          </div>
        </div>
      )}

      {tab === "upload" && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`cursor-pointer rounded-2xl border-2 border-dashed bg-[#F0FAF6] p-8 transition-all duration-250 ease-smooth hover:bg-teal-light/80 hover:shadow-card-hover ${
            isDragging ? "animate-ring-glow border-teal bg-teal-light/90 ring-2 ring-teal/30" : "border-teal/50"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleFileSelect}
          />
          <div className="flex flex-col items-center justify-center">
            <div className="mb-4 flex h-12 w-12 items-center justify-center text-teal">
              <Upload className="h-12 w-12" strokeWidth={1.5} />
            </div>
            <p className="font-medium text-zinc-700">Tap or drag a photo here</p>
            <p className="mt-1 text-xs text-zinc-500">
              JPEG, PNG or WebP · max 10 MB · at least 224×224 px
            </p>
          </div>
        </div>
      )}

      {capturedDataUrl && (
        <div className="card-static space-y-4 animate-slide-up">
          <p className="text-sm font-semibold text-zinc-800">Preview</p>
          <div className="overflow-hidden rounded-xl bg-zinc-100">
            <img
              src={capturedDataUrl}
              alt="Captured"
              className="h-52 w-full object-contain"
            />
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setCapturedDataUrl(null)}
              className="btn-secondary flex-1"
            >
              Retake
            </button>
            <RippleButton
              onClick={() => handleAnalyse(capturedDataUrl)}
              className="btn-primary flex-1"
            >
              Analyse
            </RippleButton>
          </div>
        </div>
      )}
    </div>
  );
}
