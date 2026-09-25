# SpectralLock — iPhone & Android

Apply a spectral lens so faint marks on a photograph are easier to see.

**Author:** Aziel Eliab

## Start

1. From `mobile/`: `flutter pub get`
2. `flutter run`
3. Choose **Add file**, then a lens.

Offline. No analytics. Light and dark follow the system. Application id: `com.azieeliab.spectrallock`

The phone view is a color-matrix approximation of Rosetta spectral analysis (same lens names as Corpus OCR). The full pipeline is the Python package.

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

Rosetta spectral analysis approximation. Synthetic UV, candle, indent, and
lemon are looks made from the photograph. Balance never invents marks.
The human still reads the page.

## Desktop package (counted download)

The full pipeline is the desktop package: `spectrallock ui`.

# → https://spectrallock-download-tracker.vibelock.workers.dev/ ←

GitHub: https://github.com/AzielEliab/spectrallock

**Forks are welcome and always allowed.**
