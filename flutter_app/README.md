# OfferGuard Flutter client

## Setup

Generate the platform templates once with the Flutter SDK:

```bash
flutter create --platforms=android,ios,web .
flutter pub get
```

## Run

```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

Android emulator:

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

For a deployed backend, replace the value with your HTTPS API URL.
