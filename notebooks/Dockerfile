FROM jupyter/datascience-notebook

WORKDIR /work

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["jupyter", "notebook"]
