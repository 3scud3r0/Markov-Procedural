#!/usr/bin/env bash
set -euo pipefail
validation_dir=$(cd -- "$(dirname -- "$0")" && pwd)
project_dir=$(cd -- "$validation_dir/.." && pwd)
reference_dir="$validation_dir/reference"
cp "$project_dir"/original/source/*.cs "$reference_dir/"
rm "$reference_dir/Program.cs"
dotnet build "$reference_dir/Reference.csproj" -c Release -o "$reference_dir/bin"
python "$validation_dir/run_suite.py"
python "$validation_dir/compare.py"
