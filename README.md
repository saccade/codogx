# codogx

Programs and simple data for the straight→ mechanics / dog math project.

The [physics harness](physics_harness/README.md) provides shared cases and reports while keeping the implementations independent. It currently contains three Codex check implementations; Claude originals are explicitly marked missing.

```sh
python -m pip install -r physics_harness/requirements.txt
python physics_harness/run.py check --implementation codex
python -m unittest discover -s physics_harness/tests -v
```

See [the contract](physics_harness/CONTRACT.md) to add an independent implementation. An unchanged run reuses checked results from cache. Rendering remains a separate concern and can use existing tools.
