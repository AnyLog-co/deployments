# Set docker credentials for Kubernetes & Helm
if [[ $# -eq 1 ]]
then
  DOCKER_PASSWORD=$1
else
  echo "Missing Docker password for downloading AnyLog code"
  exit 1
fi

DOCKER_REGISTRY_SERVER=docker.io
DOCKER_USER=anyloguser
DOCKER_EMAIL=anyloguser@anylog.co
kubectl create secret docker-registry imagepullsecret \
  --docker-server=${DOCKER_REGISTRY_SERVER} \
  --docker-username=${DOCKER_USER} \
  --docker-password=${DOCKER_PASSWORD} \
  --docker-email=${DOCKER_EMAIL}
