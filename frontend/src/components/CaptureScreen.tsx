"use client";

import { useCallback, useRef, useState } from "react";
import Webcam from "react-webcam";
import {
  validateImageFile,
  validateDataUrlDimensions,
  type ValidationResult,
} from "@/lib/validation";
import { useSessionStore } from "@/store/sessionStore";
import { LoadingScreen } from "./LoadingScreen";

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
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const getOrCreateSessionId = useSessionStore((s) => s.getOrCreateSessionId);

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
    <div className="mx-auto max-w-lg space-y-4">
      <div className="flex rounded-xl bg-slate-200 p-1">
        <button
          type="button"
          onClick={() => setTab("camera")}
          className={`flex-1 rounded-lg py-2 text-sm font-medium transition ${
            tab === "camera"
              ? "bg-white text-slate-800 shadow"
              : "text-slate-600"
          }`}
        >
          Live camera
        </button>
        <button
          type="button"
          onClick={() => setTab("upload")}
          className={`flex-1 rounded-lg py-2 text-sm font-medium transition ${
            tab === "upload"
              ? "bg-white text-slate-800 shadow"
              : "text-slate-600"
          }`}
        >
          Upload photo
        </button>
      </div>

      {validationError && (
        <div className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
          {validationError}
        </div>
      )}

      {cameraError && tab === "camera" && (
        <div className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
          {cameraError} Use the Upload tab if you prefer to use a photo file.
        </div>
      )}

      {tab === "camera" && (
        <div className="relative overflow-hidden rounded-2xl bg-slate-900">
          <div className="relative aspect-[4/3]">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              onUserMediaError={() =>
                setCameraError(
                  "Camera access denied. Enable the camera in your browser or device settings."
                )
              }
              className="absolute inset-0 h-full w-full object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="h-56 w-44 rounded-full border-4 border-white/60 bg-transparent" />
            </div>
          </div>
          <div className="p-4">
            <button
              type="button"
              onClick={handleCapture}
              className="w-full rounded-xl bg-white py-3 font-medium text-slate-800"
            >
              Capture
            </button>
          </div>
        </div>
      )}

      {tab === "upload" && (
        <div
          className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 p-8"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleFileSelect}
          />
          <p className="text-slate-600">Tap to choose a photo</p>
          <p className="mt-1 text-sm text-slate-500">
            JPEG, PNG or WebP, max 10 MB, at least 224×224 px
          </p>
        </div>
      )}

      {capturedDataUrl && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-700">Preview</p>
          <div className="relative overflow-hidden rounded-xl bg-slate-200">
            <img
              src={capturedDataUrl}
              alt="Captured"
              className="h-48 w-full object-contain"
            />
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setCapturedDataUrl(null)}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm"
            >
              Retake
            </button>
            <button
              type="button"
              onClick={() => handleAnalyse(capturedDataUrl)}
              className="flex-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
            >
              Analyse
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
