### Library to autograde exercises in files of type ipynb

#### Passo a passo da publicação no pypi
1. Fazer alguma alteração no código fonte;
2. Entrar no diretorio autograde e executar o script compile.sh

```./compile.sh```
3. Dar um push para o github
4. Executar, no colab, os comandos do arquivo comandos_compilacao_colab.txt. Isso vai gerar uma shared library.
   Esses comandos copiam o arquivo autograde.so para o drive
5. Fazer o download do arquivo autograde.so e colocar na pasta ipynb_autograde
6. Executar o script package.sh alterando a versao da tag do repositorio/biblioteca
```
./package.sh 0.0.21 "incremental improvements"
```
7. Preencher o login e senha da publicação no pypi