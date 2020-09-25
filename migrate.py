#! /usr/bin/env python3

import yaml
import subprocess
import os
import shutil

def load_config():
  with open("config.yaml") as config:
    parsed_yaml = yaml.load(config, Loader=yaml.FullLoader)
  return parsed_yaml

def delete_old_manifests():
  manifests_path = []
  [shutil.rmtree(d) for d in os.listdir('.') if d.startswith('manifests-')]

def download_manifests():
  print("\n\nDownloading manifests for selected certified operators... \n\n")
  cmd = ["offline-cataloger", "generate-manifests", "certified-operators"]
  process = subprocess.Popen(cmd)
  output = process.communicate()[0]
  process.wait()
  print("Done.")
  manifests_path = []
  [manifests_path.append(d) for d in os.listdir('.') if d.startswith('manifests-')]
  return manifests_path[0]

def select_bundles(manifests_path, config):

  selected_operators = config["selected_operators"]
  print("\n\n Selected bundles to migrate are: \n\n")

  for operator in selected_operators:
    print("                " + operator)

  print("\n\n")

  bundles = []
  [bundles.append(bundle) for bundle in os.listdir(manifests_path)]
  for bundle in bundles:
    if bundle not in selected_operators:
      shutil.rmtree(manifests_path + "/" + bundle)

def nest_flat_operators(manifests_path, config):

  print("nesting selected flat paths\n\n")

  flat_paths = config["flat_operators"]
  for operator in flat_paths:
    os.rename(manifests_path + "/" + operator, manifests_path + "/" + operator + "-flat")
    cmd = ["operator-courier", "nest", manifests_path + "/" + operator + "-flat", manifests_path + "/" + operator]
    process = subprocess.Popen(cmd)
    output = process.communicate()[0]
    process.wait()
    print("nesting " + operator + " ......... Done.")

def main():

  delete_old_manifests()

  config = load_config()
  manifests_path = download_manifests()

  select_bundles(manifests_path, config)
  nest_flat_operators(manifests_path, config)

if __name__ == "__main__":
  main()