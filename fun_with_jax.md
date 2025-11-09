---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Fun with JAX

**Author:** [John Stachurski](https://johnstachurski.net)

November 2025

This is a super quick illustration of the power of [JAX](https://github.com/google/jax), a Python library built by Google Research.

It should be run on a machine with a GPU --- for example, try Google Colab with the runtime environment set to include a GPU.

The aim is just to give a small taste of high performance computing in Python -- details will be covered later in the course.

We start with some imports

```python
import numpy as np
import jax
import jax.numpy as jnp
import matplotlib.pyplot as plt
```

Let's check our hardware:

```python
!nvidia-smi
```

```python
!lscpu -e
```

## Transforming Data


A very common numerical task is to apply a transformation to a set of data points.

Our transformation will be the cosine function.


Here we evaluate the cosine function at 50 points.

```python
x = np.linspace(0, 10, 50)
y = np.cos(x)
```

Let's plot.

```python
fig, ax = plt.subplots()
ax.scatter(x, y)
plt.show()
```

Our aim is to evaluate the cosine function at many points.

```python
n = 50_000_000
x = np.linspace(0, 10, n)
```

### With NumPy

```python
%%time 

y = np.cos(x)
```

```python
%%time 

y = np.cos(x)
```

```python
x = None  
```

### With JAX

```python
x_jax = jnp.linspace(0, 10, n)
```

Let's time it.


```python
%%time
    
y = jnp.cos(x_jax)
jax.block_until_ready(y);  
```

```python
%%time
    
y = jnp.cos(x_jax)
jax.block_until_ready(y); 
```

Here we change the input size --- can you explain why the timing changes?

```python
x_jax = jnp.linspace(0, 10, n + 1)
```

```python
%%time
    
y = jnp.cos(x_jax)
jax.block_until_ready(y);
```

```python
%%time
    
y = jnp.cos(x_jax)
jax.block_until_ready(y);
```

```python
x_jax = None  # Free memory
```

## Evaluating a more complicated function

```python
def f(x):
    y = np.cos(2 * x**2) + np.sqrt(np.abs(x)) + 2 * np.sin(x**4) - 0.1 * x**2
    return y
```

```python
fig, ax = plt.subplots()
x = np.linspace(0, 10, 100)
ax.plot(x, f(x))
ax.scatter(x, f(x))
plt.show()
```

Now let's try with a large array.


### With NumPy

```python
n = 50_000_000
x = np.linspace(0, 10, n)
```

```python
%%time 

y = f(x)
```

```python
%%time 

y = f(x)
```

### With JAX

```python
def f(x):
    y = jnp.cos(2 * x**2) + jnp.sqrt(jnp.abs(x)) + 2 * jnp.sin(x**4) - x**2
    return y
```

```python
x_jax = jnp.linspace(0, 10, n)
```

```python
%%time 

y = f(x_jax)
jax.block_until_ready(y);
```

```python
%%time 

y = f(x_jax)
jax.block_until_ready(y)
```

### Compiling the Whole Function

```python
f_jax = jax.jit(f)
```

```python
%%time 

y = f_jax(x_jax)
jax.block_until_ready(y);
```

```python
%%time 

y = f_jax(x_jax)
jax.block_until_ready(y);
```
