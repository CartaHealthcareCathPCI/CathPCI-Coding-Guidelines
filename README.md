# NCDR CathPCI Coding Guidelines Repository

A comprehensive, searchable web-based repository for NCDR CathPCI coding guidelines, integrating official documentation from multiple NCDR sources.

## Features

### Multi-Source Integration
- **Data Dictionary**: Full NCDR CathPCI Registry Data Dictionary specifications
- **Additional Coding Directives (FAQs)**: Official coding clarifications and FAQs
- **Questions from your Peers**: Quarterly peer questions and NCDR responses
- **Supplemental Dictionary**: Pending data element updates and clarifications

### Advanced Search Capabilities
- **Keyword Search**: Search across all content fields (questions, answers, definitions, rationales)
- **Sequence Number Search**: Dedicated search by Seq # for quick data element lookup
- **Source Filtering**: Filter by specific source document or view all
- **Real-time Results**: Instant filtering as you type

## Quick Start

### Viewing Locally
1. Open `index.html` in any modern web browser
2. All three files must be in the same directory

### Hosting on GitHub Pages
1. Create repository and upload files
2. Enable GitHub Pages in Settings → Pages
3. Site will be available at `https://YOUR-USERNAME.github.io/REPO-NAME/`

## Data Sources

| Source Document | Entries | Last Updated |
|----------------|---------|--------------|
| Additional Coding Directives (FAQs) | 145 | 2018-2020 |
| Questions from your Peers | 38 | March 2025 |
| Supplemental Dictionary | 26 | January 2025 |

## Usage Examples

- **Sequence Search**: Type `7400` to find "Indications for Cath Lab Visit"
- **Keyword Search**: Search `"bleeding"` for all bleeding-related guidance
- **Filter**: Select source document to view only those entries
- **Combined**: Filter + Search for targeted results

## Updating Data

Run `process_ncdr_data.py` to regenerate `ncdr_guidelines_data.json` from source files.

---

**Maintained by**: Carta Healthcare Abstraction Team  
**Version**: 1.0 • January 2026
