# data-files

## install

git clone \<me\>

```bash
cd data-files
python<version> -m venv data-files-venv
source data-files-venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

streamlit run app.py
```

### DONE
* recall the pattern name after having loaded one, and saving also ^^
* change action order in a circular buttons way
* add button to export (without pandas dataframe:index )
#### helpers for actions
* change dtype column in dataframe  
* save dtype step details

### TODO
#### helpers for actions
* many read cases/engine are available for excel files, each has it own behavior, this is really annoying  
* change column order  
* rename column  
* improve export/download behavior with cache if possible  
* ...  
a new warning in console :  
Warning: The DataFrame has column names of mixed type. They will be converted to strings and not roundtrip correctly.  
  table = pa.Table.from_pandas(df)  
