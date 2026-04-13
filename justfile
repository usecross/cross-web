# Cross Web repository tasks

default:
    @just --list

deploy:
    (cd website && bun run build)
    uv run fastapi deploy
