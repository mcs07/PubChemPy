(pandas)=

# *pandas* integration

## Installing *pandas*

*pandas* must be installed to use its functionality from within PubChemPy. It is an optional dependency, so it is not installed automatically with PubChemPy. The easiest way is to use pip:

```bash
pip install pandas
```

See the [pandas documentation](https://pandas.pydata.org/pandas-docs/stable/) for more information.

## Usage

It is possible for {func}`~pubchempy.get_compounds`, {func}`~pubchempy.get_substances` and {func}`~pubchempy.get_properties` to return a pandas DataFrame:

```python
df1 = pcp.get_compounds('C20H41Br', 'formula', as_dataframe=True)
df2 = pcp.get_substances([1, 2, 3, 4], as_dataframe=True)
df3 = pcp.get_properties(['smiles', 'xlogp', 'rotatable_bond_count'], 'C20H41Br', 'formula', as_dataframe=True)
```

An existing list of {class}`~pubchempy.Compound` objects can be converted into a dataframe, optionally specifying the desired columns:

```python
cs = pcp.get_compounds('C20H41Br', 'formula')
df4 = pcp.compounds_to_frame(cs, properties=['smiles', 'xlogp', 'rotatable_bond_count'])
```
