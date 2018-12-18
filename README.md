# Monitor - Lambda

## Cliente

- Instalarlo en la RaspberryPi
- Agregarlo al Crontab:

```
# crontab -e

*/2 * * * * python $HOME/dev/monitor_lambda/client.py
```

### Servidor

- Instalar `serverless`: `npm i -g serverless`
- Configurar credenciales AWS: `serverless config credentials -p aws -k $AWS_ACCESS_KEY_ID -s $AWS_SECRET_ACCESS_KEY -o`
- Exportar credenciales de Contentful: `export $(cat .env | xargs)`
- Deployar servicios: `serverless deploy`

#### Status Server

- Actualizar la URL del servicio en Contentful

#### Monitor de Connectividad

- Se configura automaticamente al deployar
