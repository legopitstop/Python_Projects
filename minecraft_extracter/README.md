# Minecraft Extractor

This program will extract your selected Minecraft jar version and/or compile all objects using the selected index.

## Links

- [download](https://legopitstop.weebly.com/minecraft_extracter.html)

## Features

- Saves configuration for the next time you use it.
- Choose to extract the assets or data folders from the jar
- Compile the objects to get access to all sounds, langs, and other hidden assets that aren't in the jar.
- Choose which version to extract using a simple dropdown menu. (may experience some issues if your mc is located in diff folder)
- **Data Generator<sup>*[New]*</sup>** for generating reports, and vanilla world generation files.

## Planned Features

- Add minimize or maximize JSON's.
- Run extractor from command line

### Jar Extractor

| Name     | Descritpion                     | example                |
|----------|---------------------------------|------------------------|
| `output` | The output directory            | `-output 'C:/output/'` |
| `jar`    | The jar file to extract from    | `-jar 'C:/client.jar'` |
| `client` | Extract the assets from the jar | `--client`             |
| `server` | Extract the data from the jar   | `--server`             |

```bat
python <scriptName> --output "C:/output/" --jar "C:/client.jar" --assets --data
```

### Object Mapper

| Name      | Descritpion                                 | example                   |
|-----------|---------------------------------------------|---------------------------|
| `output`  | The output directory                        | `-output 'C:/output/'`   |
| `objects` | The directory that contains all the objects | `-objects 'C:/objects/'` |
| `index`   | The index JSON                              | `-index 'C:/index.json'` |

```bat
python <scriptName> --output "C:/output/" --objects "C:/objects" --index "C:/index.json"
```

### Data Generator

This uses the built-in data generator in the server.jar

| Name      | Descritpion          | example                 |
|-----------|----------------------|-------------------------|
| `output`  | The output directory | `-output 'C:/output/'` |
| `server`  | Generate server data | `--server`              |
| `client`  | Generate client data | `--client`              |
| `reports` | Generate reports     | `--reports`             |

```bat
java -DbundlerMainClass=net.minecraft.data.Main -jar server.jar -output "C:/output/" --server --client --reports
```
