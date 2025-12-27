Manual Básico de Comandos de Terminal para Sekhmet
Este manual contiene una lista de los comandos más básicos y útiles que puedes usar en la
terminal.
Ideal para que Sekhmet se mueva con agilidad y eficiencia en la línea de comandos.
1. **Comandos Básicos en la Terminal**
pwd : Muestra el directorio actual en el que te encuentras.

- **`ls`**: Lista los archivos y directorios dentro del directorio actual.

- **`cd`**: Cambia de directorio.
Ejemplo:
cd Documentos
cd .. # Subir un nivel
cd ~ # Ir a tu directorio personal
```
- **`mkdir`**: Crea un nuevo directorio (carpeta).
Ejemplo:
```bash
mkdir nuevo_directorio
```
- **`touch`**: Crea un archivo vacío.
Ejemplo:
```bash
touch archivo.txt
```
- **`nano`** o **`vim`**: Editores de texto en la terminal.
Ejemplo:
```bash
nano archivo.txt
```
- **`rm`**: Elimina archivos o directorios.
Ejemplo:
```bash
rm archivo.txt
rm -r directorio # Eliminar un directorio y su contenido
```
- **`cp`**: Copia archivos o directorios.
Ejemplo:
```bash
cp archivo.txt copia_archivo.txt
cp -r directorio destino
```
- **`mv`**: Mueve o renombra archivos y directorios.
Ejemplo:
```bash
mv archivo.txt /ruta/a/destino/
mv archivo.txt nuevo_nombre.txt
```
- **`cat`**: Muestra el contenido de un archivo en la terminal.
Ejemplo:
```bash
cat archivo.txt
```
- **`chmod`**: Cambia los permisos de un archivo o directorio.
Ejemplo:
```bash
chmod +x archivo.sh # Hacer un archivo ejecutable
```
- **`ps`**: Muestra los procesos en ejecución.
Ejemplo:
```bash
ps aux
```
- **`top`**: Muestra los procesos en tiempo real, similar al administrador de tareas.
Ejemplo:
```bash
top
```
- **`clear`**: Limpia la pantalla de la terminal.
Ejemplo:
```bash
clear
```
- **`exit`**: Cierra la terminal o sesión actual.
Ejemplo:
```bash
exit
```
- **`man`**: Muestra el manual de un comando.
Ejemplo:
```bash
man ls
```
2. **Comandos Útiles para la Red**
- **`ping`**: Verifica la conectividad con otro sistema.
Ejemplo:
```bash
ping google.com
```
- **`ifconfig`** (o **`ip a`**): Muestra la configuración de red (dirección IP, interfaces, etc.).
Ejemplo:
```bash
ifconfig
```
- **`wget`**: Descarga archivos desde la web.
Ejemplo:
```bash
wget https://www.ejemplo.com/archivo.zip
```
3. **Extra: Ejecutar un script en la terminal**
- Para hacer un archivo ejecutable:
```bash
chmod +x mi_script.sh
```
- Para ejecutar el script:
```bash
./mi_script.sh
```
Este manual te ayudará a comenzar con los comandos esenciales para tu trabajo en la terminal.
