# Voice Assistant

Simple example of offline voice assistant.

## Run

Before start it's necessarily to download Llama model to `llama` directory. Assistant can use any LLM's which
supported by [llama.cpp](https://github.com/ggerganov/llama.cpp). For Russian language it's better to use
[Saiga/Mistral](https://huggingface.co/IlyaGusev/saiga_mistral_7b_gguf/tree/main) by Ilya Gusev.

To start assistant with basic settings use following command:

```bash
python3 main.py "llama/model-q4_K.gguf" --device cuda
```

## Installation

For CPU or NVidia platforms use following instructions to initialize virtual environment:

```bash
python3 -m venv venv # create virtual environment, if needed
source venv/bin/activate # activate virtual environment, if needed
python3 -m pip install -r requirements.txt
```

For AMD platform use following commands:

```bash
python3 -m venv venv # create virtual environment, if needed
source venv/bin/activate # activate virtual environment, if needed
python3 -m pip install --pre torch torchvision torchaudio --index-url 'https://download.pytorch.org/whl/nightly/rocm5.7/' 
python3 -m pip install -r requirements.txt
```

Assistant use `ffplay` (from `ffmpeg`) to play generated speech. This program must be accessible in `PATH` directories.

## NLTK Data Directory

After installation you need to download data for NLTK stemmer. It can be done using following command:

```bash
python3 -c "import nltk ; nltk.download('punkt')"

```

By default NLTK will save all downloaded files to `$HOME` directory. If it's necessarily to define another location use
`NLTK_DATA` environment variables:

```bash
NLTK_DATA=nltk_data/ python3 -c "import nltk ; nltk.download('punkt')"
```

Where `nltk_data` - directory for NLTK files.

## License

Source code is primarily distributed under the terms of the MIT license. See LICENSE for details.
