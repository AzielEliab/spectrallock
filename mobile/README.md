# SpectralLock — iPhone & Android

Pick a photograph of a manuscript page. Apply a named overlay
(zero / tazel / vyrn / uv / rosetta / zen / chaos / balance) using a
simple Dart color-matrix that approximates the published hues.

Offline. No analytics. Dark matte / gold.

Application id: `com.azieeliab.spectrallock`

This is **not** the full Python pipeline (no histogram equalization,
no band-pass, no 256-px hosted preview). Color-matrix approximation of
Rosetta spectral analysis. Same lens names as Corpus OCR.

## Open in Android Studio / Xcode

The `android/` and `ios/` folders here are skeleton READMEs because
this tree was written without the Flutter SDK on PATH.

```bash
cd mobile
flutter create --org com.azieeliab --project-name spectrallock .
flutter pub get
flutter run
```

Then open `android/` in Android Studio, or `ios/Runner.xcworkspace` in
Xcode.

## Honest scope

Rosetta spectral analysis approximation. Synthetic UV is a look, not a
lamp. Balance never invents marks. The human still reads the page.

## Desktop package (counted download)

This phone app does not replace the desktop package.

# → https://spectrallock-download-tracker.vibelock.workers.dev/ ←

GitHub: https://github.com/AzielEliab/spectrallock

**Forks are welcome and always allowed.**
