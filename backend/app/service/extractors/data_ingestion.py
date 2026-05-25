import time

from app.core.extractor_repository import store_results
from app.core.data_unified_repository import store_unified_results


def run_ingestion(resources, sources):
    for source in sources:
        config = resources[source]
        extractor = config["extractor"]
        converter = config["to_job_dto"]

        print(f"\n--- Iniciando extracción: {source.upper()} ---\n")

        for target in config["targets"]:
            query = target["query"]
            params = target["params"]

            print(f"[{source}] Buscando: {query}")
            results = extractor(query, **params)
            print(f"[{source}] Encontrados: {len(results)}")

            if results:
                source_label = {"linkedin": "LinkedIn", "jsearch": "JSearch", "activejobsdb": "ActiveJobsDB"}.get(source.lower(), source.capitalize())
                store_results(results, source_label, query)
                dtos = [converter(r, query) for r in results]
                store_unified_results([d.to_dict() for d in dtos], source_label, query)

            print(f"[{source}] Esperando 10 segundos...")
            time.sleep(10)

    print("\n--- Ingestion completa ---")
