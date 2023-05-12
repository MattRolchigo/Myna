#!/bin/bash

# Check if need to set default directory values
if [ -z "$CLASSIFICATION_DIR" ]; then
  CLASSIFICATION_DIR="$(cd ../..; pwd)/classification"
fi

# Clone and build if necessary
ROOT_DIR=$(pwd)
TARGET_COMMIT="8cdd8133c21e197d7937dc7721872eb69762542e"
if [ -d "$CLASSIFICATION_DIR" ]; then
  echo "$CLASSIFICATION_DIR already exists."
  cd $CLASSIFICATION_DIR
  COMMIT=$(git rev-parse HEAD)
  if [ $COMMIT != $TARGET_COMMIT ]; then
    echo "WARNING: Version of target classification repository"
    echo "does not match recommended value"
    echo "  -- Recommended commit: $TARGET_COMMIT"
    echo "  -- Specified repo commit: $COMMIT"
  fi
else
  echo "Cloning classification repository to $CLASSIFICATION_DIR"
  cd ..
  git clone https://code.ornl.gov/ygk/classification.git
  cd classification
  git branch -u origin/myna myna
  git switch myna
  git checkout $TARGET_COMMIT
fi

# 
PACKAGE=`conda list | awk -F"[ ',]+" '/^classification/{print $1}'`
if [ $PACKAGE = "classification" ]; 
then
  echo "classification package already installed."
else
  echo "Installing classification package"
  cd $CLASSIFICATION_DIR
  pip install -e .
fi

cd $ROOT_DIR