import 'package:flutter_test/flutter_test.dart';
import 'package:offerguard_app/main.dart';

void main() {
  testWidgets('renders OfferGuard', (tester) async {
    await tester.pumpWidget(const OfferGuardApp());
    expect(find.text('OfferGuard'), findsOneWidget);
    expect(find.text('Assess a recruitment message'), findsOneWidget);
  });
}
