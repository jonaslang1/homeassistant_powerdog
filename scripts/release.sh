#!/bin/bash

RELEASE_VERSION=$(buildkite-agent meta-data get release-version)
RELEASE_NOTES=$(buildkite-agent meta-data get release-notes)

echo "+++ :rocket: Releasing version ${RELEASE_VERSION}"

touch custom_components/powerdog/${RELEASE_VERSION}

cd custom_components &&\
zip -r powerdog.zip \
    powerdog \
    -x "*/__pycache__/*"

gh release create \
    ${RELEASE_VERSION} \
    'powerdog.zip' \
    -t ${RELEASE_VERSION} \
    -n "${RELEASE_NOTES}" \
    --repo 'jonaslang1/homeassistant_powerdog'
