pygame_wasm:
    uv run pygbag pygame_examples 

pygame_itchio:
    uv run pygbag --archive --template noctx.tmpl --ume_block 0 pygame_examples

serve_docs:
    uv run python -m http.server

clean:
    find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf