import 'dart:convert';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

const apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000');

void main() => runApp(const OfferGuardApp());

class OfferGuardApp extends StatelessWidget {
  const OfferGuardApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'OfferGuard',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      brightness: Brightness.dark,
      useMaterial3: true,
      scaffoldBackgroundColor: const Color(0xFF07111F),
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF38BDF8),
        brightness: Brightness.dark,
      ),
    ),
    home: const AssessmentPage(),
  );
}

class AssessmentPage extends StatefulWidget {
  const AssessmentPage({super.key});
  @override
  State<AssessmentPage> createState() => _AssessmentPageState();
}

class _AssessmentPageState extends State<AssessmentPage> {
  final textController = TextEditingController();
  bool loading = false;
  bool explain = true;
  bool officialListingVerified = false;
  String language = 'en';
  String? fileName;
  Uint8List? fileBytes;
  String? error;
  Map<String, dynamic>? result;

  @override
  void dispose() {
    textController.dispose();
    super.dispose();
  }

  Future<void> chooseFile() async {
    final picked = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'png', 'jpg', 'jpeg'],
    );
    if (picked.isEmpty) return;

    final file = picked.first;
    final declaredSize = await file.length();
    if (declaredSize != null && declaredSize > 10 * 1024 * 1024) {
      setState(() => error = 'Choose a file up to 10 MB.');
      return;
    }

    final bytes = await file.readAsBytes();
    if (bytes.length > 10 * 1024 * 1024) {
      setState(() => error = 'Choose a file up to 10 MB.');
      return;
    }

    setState(() {
      fileName = file.name;
      fileBytes = bytes;
      result = null;
      error = null;
    });
  }

  Future<void> assess() async {
    if (textController.text.trim().isEmpty && fileBytes == null) {
      setState(() => error = 'Paste a message or choose a PDF/PNG/JPEG file.');
      return;
    }

    setState(() {
      loading = true;
      error = null;
      result = null;
    });

    try {
      late http.Response response;
      if (fileBytes != null) {
        final request = http.MultipartRequest(
          'POST',
          Uri.parse(apiBaseUrl + '/api/assess-file'),
        );
        request.fields['language'] = language;
        request.fields['explain'] = explain.toString();
        request.fields['official_listing_verified'] = officialListingVerified.toString();
        request.files.add(
          http.MultipartFile.fromBytes('file', fileBytes!, filename: fileName),
        );
        response = await http.Response.fromStream(
          await request.send().timeout(const Duration(seconds: 60)),
        );
      } else {
        response = await http.post(
          Uri.parse(apiBaseUrl + '/api/assess'),
          headers: const {'Content-Type': 'application/json'},
          body: jsonEncode({
            'text': textController.text.trim(),
            'language': language,
            'official_listing_verified':
                officialListingVerified ? true : null,
            'explain': explain,
          }),
        );
      }

      final body = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode >= 400) {
        throw Exception((body['detail'] ?? 'Request failed').toString());
      }
      setState(() => result = body);
    } catch (e) {
      setState(() => error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  void reset() {
    setState(() {
      textController.clear();
      fileName = null;
      fileBytes = null;
      error = null;
      result = null;
      officialListingVerified = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                Row(
                  children: [
                    Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        gradient: const LinearGradient(
                          colors: [Color(0xFF38BDF8), Color(0xFF8B5CF6)],
                        ),
                      ),
                      child: const Icon(
                        Icons.verified_user_outlined,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'OfferGuard',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          Text(
                            'Evidence-first job-offer risk assessment',
                            style: TextStyle(color: Color(0xFFAFC2D8)),
                          ),
                        ],
                      ),
                    ),
                    DropdownButton<String>(
                      value: language,
                      underline: const SizedBox.shrink(),
                      dropdownColor: const Color(0xFF102137),
                      items: const [
                        DropdownMenuItem(
                          value: 'en',
                          child: Text('English'),
                        ),
                        DropdownMenuItem(
                          value: 'te',
                          child: Text('తెలుగు'),
                        ),
                        DropdownMenuItem(
                          value: 'hi',
                          child: Text('हिन्दी'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) setState(() => language = value);
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [Color(0xFF10243A), Color(0xFF0A1727)],
                    ),
                    border: Border.all(color: Color(0x2267E8F9)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.auto_awesome, color: Color(0xFF67E8F9), size: 28),
                      const SizedBox(width: 14),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Check. Understand. Compare.',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                            ),
                            SizedBox(height: 5),
                            Text(
                              'Get evidence for this offer, then explore comparable employers through their official career sites.',
                              style: TextStyle(color: Color(0xFFAFC2D8), height: 1.35),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: const [
                        Icon(Icons.shield_outlined, color: Color(0xFF67E8F9)),
                        SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Evidence first. Uncertainty is visible. AI never decides the outcome.',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                LayoutBuilder(
                  builder: (context, constraints) {
                    final input = buildInput();
                    final panel = ResultPanel(result: result);
                    if (constraints.maxWidth < 900) {
                      return Column(
                        children: [input, const SizedBox(height: 16), panel],
                      );
                    }
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: input),
                        const SizedBox(width: 16),
                        Expanded(child: panel),
                      ],
                    );
                  },
                ),
                if (error != null) ...[
                  const SizedBox(height: 14),
                  Card(
                    color: const Color(0xFF2A1416),
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline, color: Colors.redAccent),
                          const SizedBox(width: 10),
                          Expanded(child: Text(error!)),
                        ],
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: 20),
                const Text(
                  'OfferGuard is assistive. Independently verify employers and roles before paying or sharing sensitive information.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF6F8398), fontSize: 12),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget buildInput() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Assess a recruitment message',
              style: TextStyle(fontSize: 19, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Text(
              'Paste text or attach a PDF, PNG, or JPEG offer.',
              style: TextStyle(color: Color(0xFFAFC2D8)),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: textController,
              minLines: 9,
              maxLines: 14,
              decoration: const InputDecoration(
                hintText: 'Paste the recruiter message, email, or offer text...',
                filled: true,
                fillColor: Color(0xFF081522),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(14)),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                OutlinedButton.icon(
                  onPressed: loading ? null : chooseFile,
                  icon: const Icon(Icons.attach_file),
                  label: Text(fileName ?? 'Choose file'),
                ),
                const SizedBox(width: 8),
                const Text(
                  '10 MB max',
                  style: TextStyle(color: Color(0xFF6F8398)),
                ),
              ],
            ),
            SwitchListTile.adaptive(
              contentPadding: EdgeInsets.zero,
              value: officialListingVerified,
              onChanged: (value) =>
                  setState(() => officialListingVerified = value),
              title: const Text(
                'I independently verified the exact role on the official careers site',
              ),
              subtitle: const Text(
                'This is a user-supplied check; OfferGuard does not perform the lookup.',
              ),
            ),
            SwitchListTile.adaptive(
              contentPadding: EdgeInsets.zero,
              value: explain,
              onChanged: (value) => setState(() => explain = value),
              title: const Text('Explain evidence with Azure OpenAI'),
            ),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: loading ? null : assess,
                    icon: loading
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.search_rounded),
                    label: Text(loading ? 'Analysing...' : 'Assess safely'),
                  ),
                ),
                const SizedBox(width: 8),
                TextButton(
                  onPressed: loading ? null : reset,
                  child: const Text('Reset'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class ResultPanel extends StatelessWidget {
  const ResultPanel({required this.result, super.key});
  final Map<String, dynamic>? result;

  @override
  Widget build(BuildContext context) {
    if (result == null) {
      return const Card(
        child: SizedBox(
          height: 450,
          child: Center(
            child: Text(
              'Your evidence chain will appear here',
              style: TextStyle(color: Color(0xFF7F95AC)),
            ),
          ),
        ),
      );
    }

    final outcome = (result!['outcome'] ?? 'UNCONFIRMED').toString();
    final evidence =
        (result!['evidence'] as List? ?? const []).cast<Map<String, dynamic>>();
    final uncertainty =
        (result!['uncertainty'] as List? ?? const []).map((e) => e.toString());
    final actions =
        (result!['actions'] as List? ?? const []).map((e) => e.toString());
    final accent = outcome == 'RISK_DETECTED'
        ? const Color(0xFFF87171)
        : outcome == 'VERIFIED'
            ? const Color(0xFF4ADE80)
            : const Color(0xFFFBBF24);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Assessment',
                    style: TextStyle(fontSize: 19, fontWeight: FontWeight.w700),
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: accent.withAlpha(35),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: accent.withAlpha(120)),
                  ),
                  child: Text(
                    outcome.replaceAll('_', ' '),
                    style: TextStyle(
                      color: accent,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Metric(
                  label: 'Risk',
                  value: (result!['risk'] ?? 'LOW').toString(),
                ),
                Metric(
                  label: 'Signals',
                  value: evidence.length.toString(),
                ),
                Metric(
                  label: 'Score',
                  value: (result!['score'] ?? 0).toString(),
                ),
              ],
            ),
            const SizedBox(height: 18),
            if (result!['ai_explanation'] is Map<String, dynamic>) ...[
              const Text(
                'Evidence summary',
                style: TextStyle(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
              _AiSummary(summary: result!['ai_explanation']),
              const SizedBox(height: 14),
            ],
            const Text(
              'Evidence',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            if (evidence.isEmpty)
              const Text(
                'No deterministic warning signal fired.',
                style: TextStyle(color: Color(0xFFAFC2D8)),
              ),
            for (final item in evidence) EvidenceTile(item: item),
            if ((result!['why'] as List? ?? const []).isNotEmpty) ...[
              const SizedBox(height: 10),
              const Text(
                'Decision chain',
                style: TextStyle(fontWeight: FontWeight.w700),
              ),
              for (final item in (result!['why'] as List? ?? const []))
                Bullet(text: item.toString(), icon: Icons.chevron_right),
            ],
            if (result!['facts'] is Map<String, dynamic>) ...[
              const SizedBox(height: 12),
              const Text(
                'Extracted facts',
                style: TextStyle(fontWeight: FontWeight.w700),
              ),
              _FactsSummary(facts: result!['facts'] as Map<String, dynamic>),
            ],
            if (result!['similar_companies'] is List && (result!['similar_companies'] as List).isNotEmpty) ...[
              const SizedBox(height: 16),
              SimilarCompanies(items: (result!['similar_companies'] as List).cast<Map<String, dynamic>>()),
            ],
            const SizedBox(height: 14),
            const Text(
              'What could not be verified',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
            for (final item in uncertainty)
              Bullet(text: item, icon: Icons.help_outline),
            const SizedBox(height: 12),
            const Text(
              'Safer next steps',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
            for (final item in actions)
              Bullet(text: item, icon: Icons.arrow_forward),
            const SizedBox(height: 12),
            Text(
              (result!['disclaimer'] ?? '').toString(),
              style: const TextStyle(
                color: Color(0xFF6F8398),
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AiSummary extends StatelessWidget {
  const _AiSummary({required this.summary});
  final Map<String, dynamic> summary;

  @override
  Widget build(BuildContext context) {
    final text = (summary['summary'] ?? '').toString();
    final actions = (summary['actions'] as List? ?? const [])
        .map((e) => e.toString())
        .where((e) => e.trim().isNotEmpty)
        .take(4)
        .toList();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0x0C67E8F9),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x1967E8F9)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (text.isNotEmpty)
            Text(text, style: const TextStyle(color: Color(0xFFD5E1ED), height: 1.4)),
          if (actions.isNotEmpty) ...[
            const SizedBox(height: 8),
            for (final item in actions)
              Bullet(text: item, icon: Icons.arrow_forward_rounded),
          ],
        ],
      ),
    );
  }
}

class _FactsSummary extends StatelessWidget {
  const _FactsSummary({required this.facts});
  final Map<String, dynamic> facts;

  @override
  Widget build(BuildContext context) {
    final emails = (facts['emails'] as List? ?? const []).map((e) => e.toString()).toList();
    final domains = (facts['link_domains'] as List? ?? const []).map((e) => e.toString()).toList();

    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF081522),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (emails.isNotEmpty) ...[
            const Text('Emails', style: TextStyle(color: Color(0xFF7F95AC), fontSize: 11)),
            const SizedBox(height: 4),
            Text(emails.join(', '), style: const TextStyle(color: Color(0xFFD5E1ED))),
          ],
          if (domains.isNotEmpty) ...[
            if (emails.isNotEmpty) const SizedBox(height: 8),
            const Text('Link domains', style: TextStyle(color: Color(0xFF7F95AC), fontSize: 11)),
            const SizedBox(height: 4),
            Text(domains.join(', '), style: const TextStyle(color: Color(0xFFD5E1ED))),
          ],
          if (emails.isEmpty && domains.isEmpty)
            const Text(
              'No email or link entities were extracted.',
              style: TextStyle(color: Color(0xFFAFC2D8)),
            ),
        ],
      ),
    );
  }
}

class SimilarCompanies extends StatelessWidget {
  const SimilarCompanies({required this.items, super.key});
  final List<Map<String, dynamic>> items;

  Future<void> openCareers(String url) async {
    final uri = Uri.tryParse(url);
    if (uri != null) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1B2B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0x1967E8F9)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.work_outline, color: Color(0xFF67E8F9), size: 19),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Comparable employers',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
              ),
            ],
          ),
          const SizedBox(height: 5),
          const Text(
            'Explore similar employers for this role. These are official career sites, not a live vacancy guarantee.',
            style: TextStyle(color: Color(0xFF7F95AC), fontSize: 12, height: 1.35),
          ),
          const SizedBox(height: 10),
          for (final item in items.take(5))
            Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 9),
              decoration: BoxDecoration(
                color: const Color(0xFF081522),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: const Color(0x1467E8F9),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      (item['company'] ?? '?').toString().substring(0, 1),
                      style: const TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF67E8F9)),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          (item['company'] ?? 'Employer').toString(),
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          (item['match'] ?? 'Comparable employer').toString(),
                          style: const TextStyle(color: Color(0xFF7F95AC), fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                  TextButton.icon(
                    onPressed: () => openCareers((item['careers_url'] ?? '').toString()),
                    icon: const Icon(Icons.open_in_new, size: 16),
                    label: const Text('Careers'),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class Metric extends StatelessWidget {
  const Metric({required this.label, required this.value, super.key});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFF081522),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(
                color: Color(0xFF7F95AC),
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ],
        ),
      );
}

class EvidenceTile extends StatelessWidget {
  const EvidenceTile({required this.item, super.key});
  final Map<String, dynamic> item;

  @override
  Widget build(BuildContext context) {
    final title =
        (item['signal'] ?? '').toString() + ' • ' + (item['name'] ?? '').toString();
    final quote = (item['quote'] ?? '').toString();
    final claim = (item['claim'] ?? '').toString();

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF081522),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 7),
          Text(
            '“' + quote + '”',
            style: const TextStyle(
              color: Color(0xFFB9C8D9),
              height: 1.4,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            claim,
            style: const TextStyle(
              color: Color(0xFF7F95AC),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

class Bullet extends StatelessWidget {
  const Bullet({required this.text, required this.icon, super.key});
  final String text;
  final IconData icon;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(top: 6),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 16, color: const Color(0xFF67E8F9)),
            const SizedBox(width: 7),
            Expanded(
              child: Text(
                text,
                style: const TextStyle(
                  color: Color(0xFFAFC2D8),
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      );
}
