FROM python:3.11

ENV PYTHONUNBUFFERED=1

ARG WORKDIR=/app
ARG USER=user

WORKDIR ${WORKDIR}

RUN useradd --system ${USER} && \
    chown --recursive ${USER} ${WORKDIR}

RUN apt update && apt upgrade -y

COPY --chown=${USER} requirements.txt requirements.txt

RUN pip install --upgrade pip && \
    pip install --requirement requirements.txt
#COPY . .
# COPY --chown=${USER} ./main_pet_project.py main_pet_project.py
# COPY --chown=${USER} ./database.py database.py
# COPY --chown=${USER} ./repository.py repository.py
# COPY --chown=${USER} ./router.py router.py
# COPY --chown=${USER} ./schemas.py schemas.py

COPY --chown=${USER} ./main.py main.py
COPY --chown=${USER} ./Makefile Makefile
COPY --chown=${USER} ./db_data db_data



USER ${USER}


ENTRYPOINT ["uvicorn", "main_pet_project:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.11-slim
#
# WORKDIR /app
#
# COPY . .
#
# RUN pip install -r requirements.txt
#
# # Убедись, что папка для базы данных существует
#
#
# CMD ["uvicorn", "main_pet_project:app", "--host", "0.0.0.0", "--port", "8000"]
