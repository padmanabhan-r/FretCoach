#!/bin/bash
cd "$(dirname "$0")"
md-to-pdf opik-usage-pdf.md && mv opik-usage-pdf.pdf opik-usage.pdf && echo "Done: opik-usage.pdf"
