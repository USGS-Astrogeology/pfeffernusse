server: 
	openapi-generator-cli.jar generate -i https://app.swaggerhub.com/apiproxy/schema/file/USGS-Astro/pfeffernusse2/0.1.3/swagger.yaml -g python-flask -c config.json

