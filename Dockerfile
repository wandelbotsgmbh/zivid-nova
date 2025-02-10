FROM python:3.11 AS builder

# install all zivid SDK and all required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx=* \
    libglib2.0-0=* && \
    wget --progress=dot:giga \
        https://downloads.zivid.com/sdk/releases/2.14.1+b4e8f261-1/u22/amd64/zivid_2.14.1+b4e8f261-1_amd64.deb \
        https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.12149.1/intel-igc-core_1.0.12149.1_amd64.deb \
        https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.12149.1/intel-igc-opencl_1.0.12149.1_amd64.deb \
        https://github.com/intel/compute-runtime/releases/download/22.39.24347/intel-level-zero-gpu-dbgsym_1.3.24347_amd64.ddeb \
        https://github.com/intel/compute-runtime/releases/download/22.39.24347/intel-level-zero-gpu_1.3.24347_amd64.deb \
        https://github.com/intel/compute-runtime/releases/download/22.39.24347/intel-opencl-icd-dbgsym_22.39.24347_amd64.ddeb \
        https://github.com/intel/compute-runtime/releases/download/22.39.24347/intel-opencl-icd_22.39.24347_amd64.deb \
        https://github.com/intel/compute-runtime/releases/download/22.39.24347/libigdgmm12_22.2.0_amd64.deb &&  \
    apt-get install -y --no-install-recommends ./*.deb && \
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /zivid-nova
COPY pyproject.toml poetry.lock ./
COPY zivid_nova/ ./zivid_nova/

# install everything into single venv
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-dev # install dependencies
RUN --mount=type=cache,target=$POETRY_CACHE_DIR  poetry run pip install .  # zivid_nova package

FROM python:3.11-slim AS runtime

ENV VIRTUAL_ENV=/zivid-nova/.venv PATH="/zivid-nova/.venv/bin:$PATH"

COPY --from=builder ./*.deb ./*.ddeb ./

# install all zivid SDK and all required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx=* \
    libglib2.0-0=* && \
    apt-get install -y --no-install-recommends ./*.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf ./*.deb ./*.ddeb


COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY static/ static/

ENTRYPOINT ["python", "-m", "zivid_nova"]