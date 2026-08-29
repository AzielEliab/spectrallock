import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'theme.dart';

const limitation =
    'Advisory overlays on a photograph you pick. Not a lab spectrometer, '
    'not real UV hardware, not forensic proof of hidden ink, not OCR, not '
    'scribal truth. Synthetic UV is a look, not a lamp. Balance never invents '
    'marks. The human still reads the page.';

/// Color-matrix approximations of the published hues. Not the Python pipeline.
const matrices = <String, List<double>>{
  'zero': [
    0.2126, 0.7152, 0.0722, 0, 0,
    0.2126, 0.7152, 0.0722, 0, 0,
    0.2126, 0.7152, 0.0722, 0, 0,
    0, 0, 0, 1, 0,
  ],
  'tazel': [
    0.70, 0.12, 0.08, 0, 0,
    0.08, 1.25, 0.18, 0, 8,
    0.05, 0.28, 1.05, 0, 4,
    0, 0, 0, 1, 0,
  ],
  'vyrn': [
    1.28, -0.12, 0.18, 0, 6,
    -0.12, 0.52, -0.05, 0, 0,
    0.18, -0.08, 1.12, 0, 4,
    0, 0, 0, 1, 0,
  ],
  'uv': [
    0.78, 0.05, 0.18, 0, 12,
    0.04, 0.72, 0.22, 0, 8,
    0.08, 0.12, 1.32, 0, 28,
    0, 0, 0, 1, 0,
  ],
  'rosetta': [
    0.85, 0.22, 0.12, 0, 4,
    0.18, 0.90, 0.14, 0, 4,
    0.12, 0.18, 0.88, 0, 6,
    0, 0, 0, 1, 0,
  ],
  'zen': [
    0.80, 0.18, 0.18, 0, 6,
    0.16, 0.88, 0.16, 0, 6,
    0.16, 0.18, 0.92, 0, 8,
    0, 0, 0, 1, 0,
  ],
  'chaos': [
    0.70, 0.10, 0.28, 0, 4,
    0.08, 0.62, 0.18, 0, 0,
    0.22, 0.10, 1.10, 0, 10,
    0, 0, 0, 1, 0,
  ],
  'balance': [
    0.78, 0.16, 0.18, 0, 5,
    0.14, 0.80, 0.16, 0, 4,
    0.16, 0.16, 0.96, 0, 8,
    0, 0, 0, 1, 0,
  ],
};

void main() {
  runApp(const SpectralLockApp());
}

class SpectralLockApp extends StatelessWidget {
  const SpectralLockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SpectralLock',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const OverlayPage(),
    );
  }
}

class OverlayPage extends StatefulWidget {
  const OverlayPage({super.key});

  @override
  State<OverlayPage> createState() => _OverlayPageState();
}

class _OverlayPageState extends State<OverlayPage> {
  final _picker = ImagePicker();
  XFile? _photo;
  String _mode = 'rosetta';

  Future<void> _pick() async {
    final shot = await _picker.pickImage(source: ImageSource.gallery);
    if (shot == null) return;
    setState(() => _photo = shot);
  }

  @override
  Widget build(BuildContext context) {
    final matrix = matrices[_mode]!;
    return Scaffold(
      appBar: AppBar(title: const Text('SpectralLock')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(limitation, style: TextStyle(color: kGold, height: 1.4)),
          const SizedBox(height: 12),
          FilledButton(onPressed: _pick, child: const Text('Pick photograph')),
          const SizedBox(height: 12),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: matrices.keys.map((id) {
              final on = id == _mode;
              return ChoiceChip(
                label: Text(id),
                selected: on,
                onSelected: (_) => setState(() => _mode = id),
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
          if (_photo != null) ...[
            const Text('Before', style: TextStyle(color: kGoldDim)),
            const SizedBox(height: 6),
            Image.file(File(_photo!.path), fit: BoxFit.contain),
            const SizedBox(height: 12),
            Text('After · $_mode (color-matrix approximation)',
                style: const TextStyle(color: kGoldDim)),
            const SizedBox(height: 6),
            ColorFiltered(
              colorFilter: ColorFilter.matrix(matrix),
              child: Image.file(File(_photo!.path), fit: BoxFit.contain),
            ),
          ],
        ],
      ),
    );
  }
}
