import 'package:flutter/material.dart';

/// SpectralLock phone theme. Light and dark follow the system. Gold focus.
const Color kPaper = Color(0xFFF4F1EA);
const Color kPaperSurface = Color(0xFFFFFCF7);
const Color kInk = Color(0xFF1C1915);
const Color kMatteBlack = Color(0xFF12110E);
const Color kSurface = Color(0xFF1C1B17);
const Color kGold = Color(0xFFC9A227);
const Color kGoldDim = Color(0xFF6D5208);
const Color kIvory = Color(0xFFF4EFE6);
const Color kOnGold = Color(0xFF1A1404);

ThemeData buildLightTheme() {
  const scheme = ColorScheme.light(
    primary: kGold,
    onPrimary: kOnGold,
    secondary: kGoldDim,
    onSecondary: kPaperSurface,
    surface: kPaperSurface,
    onSurface: kInk,
  );
  return _base(scheme, kPaper, kInk);
}

ThemeData buildAppTheme() => buildDarkTheme();

ThemeData buildDarkTheme() {
  const scheme = ColorScheme.dark(
    primary: kGold,
    onPrimary: kOnGold,
    secondary: kGold,
    onSecondary: kOnGold,
    surface: kSurface,
    onSurface: kIvory,
  );
  return _base(scheme, kMatteBlack, kIvory);
}

ThemeData _base(ColorScheme scheme, Color scaffold, Color foreground) {
  return ThemeData(
    useMaterial3: true,
    brightness: scheme.brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: scaffold,
    focusColor: kGold,
    hoverColor: const Color(0x33C9A227),
    splashColor: const Color(0x44C9A227),
    appBarTheme: AppBarTheme(
      backgroundColor: scaffold,
      foregroundColor: foreground,
      elevation: 0,
      centerTitle: false,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: kGold,
        foregroundColor: kOnGold,
        minimumSize: const Size(64, 48),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: foreground,
        minimumSize: const Size(64, 48),
      ),
    ),
  );
}
