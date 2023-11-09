COMMIT_SHA="$(git rev-parse HEAD)"
VERSION="1.3.0"
echo "Building docker image with commit sha: ${COMMIT_SHA} and version: ${VERSION}"
docker build --build-arg="COMMIT_SHA=$COMMIT_SHA" --build-arg="VERSION=$VERSION" \
  --platform linux/amd64 \
  -t mit-annotation-api:${COMMIT_SHA} .
docker tag mit-annotation-api:${COMMIT_SHA} chunwei/mitaskem-api:${VERSION}
docker push chunwei/mitaskem-api:${VERSION}