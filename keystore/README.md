# Test signing key

`test-signing.jks` signs the debug build and the CI release build, so every build from GitHub Actions carries the
same signature and installs over the previous one on a phone. Store and key password: `jyotish-test`, alias
`jyotish-test`.

It is in the repository on purpose and is **for testing only**. Never upload a build signed with it to Google Play:
the Play upload key comes from the `JYOTISH_KEYSTORE` environment variables (see the README) and must never be
committed.
