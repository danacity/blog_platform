---
title: Tobler, Broadcasting, and Maidenhead
date: 2019-07-28T10:30:00+01:00
draft: false
excerpt: My very 1st blog post (colab notebook from 2019) about how to solve a Maidenhead problem using broadcasting .
tags:
  - Geospatial
Diataxis:
  - Explanation
---
## 2019 - Tobler's 1st Law of Geography
''Everything is related to everything else. But near things are more related than distant things. - Waldo R. Tobler -1969'' 

In 2019 I was obsessed with the idea of creating a location2vector tool, what would convert a location in time into a vector representation of what it meant to be in that location at that time. This idea lasted for a few years where I amassed a huge amount of data most of it open sourced from airports, to census data, to liquor sales, commercial real estate listings, and much more. 

When I stumbled upon Maidenhead in 2019 while looking for ways to measure distances between airports and specific locations, I thought I'd found a simple solution. Little did I know this would lead me down a fascinating path of geospatial data handling and tensor operations.

Maidenhead is commonly used in amateur radio operators, and pilots. I just liked the picture, but it turns out to have some very neat properties. 
Other names for it are The QTH, the QRA, WW Grid or Maidenhead. 
Elements of the grid system 18*18 324 very large areas named fileds, each field is divited by 100 squares, and each square is divided into 576 sub-squares the Field is two letter(A-R), the square is two numbers and the sub-square is two letters(A-X). 
and because of that you can make a pretty small area with six digits that covers the whole world. You can even add two more number and two more letters to get a really small area. For a more complete example you can check out https://www.dxzone.com/grid-square-locator-system-explained/. 

![USA map maidenhead](/public/images/maidenhead.jpg)


## The Airport Problem - Where It All Started

My journey began with a straightforward question: how could I efficiently analyze the relationship between airports and their surrounding areas? In 2019, I was working with a dataset of medium and large U.S. airports:

This code probably doesn't work any more about I found a way to get the airports from ourairports.com
```python
# Get and filter airport data 
import pandas as pd # Download airport data 
!wget --header="Host: ourairports.com" --header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36" "http://ourairports.com/data/airports.csv" -O "airports.csv" df = pd.read_csv("airports.csv") 
# Clean and filter the data 
df = df.dropna(subset=["municipality", "elevation_ft", "type"]) 
df = df[df.type.str.contains('medium_airport|large_airport', regex=True)] 
df = df[(df.iso_country == "US")]  
# US airports only # Convert coordinates to numeric values 
df['latitude_deg'] = pd.to_numeric(df['latitude_deg'], errors='coerce') df['longitude_deg'] = pd.to_numeric(df['longitude_deg'], errors='coerce') print(f"Found {len(df)} medium and large US airports")`
```
I wanted a system that could help me understand the relationship between these airports and their surrounding areas. The hypothesis was simple - any location data is most relevant within a certain proximity to the point of interest, but how to efficiently calculate this proximity?
![Chicago map maidenhead](/public/images/maidenhead_chicago.png)

That's when I discovered the Maidenhead system. Looking at a Maidenhead map, I realized Chicago sits in grid cell EN61, and it seemed logical that information from adjacent cells (EN50, EN51, EN52, EN60, EN61, EN62, EN70, EN71, EN72) would all contain data relevant to understanding Chicago.

This led me to a fundamental question: How could I efficiently find all the Maidenhead locators surrounding a given point? The answer, as it turned out, would be found in the power of NumPy Broadcasting.

## The Problem: Finding Neighboring Grid Squares

My hypothesis was straightforward: When analyzing locations like Chicago (in grid EN61), information from adjacent grid cells would likely contain relevant data. I needed an efficient way to identify all these surrounding cells without writing clunky loops.

The Maidenhead system encodes locations in pairs of characters that represent increasingly precise divisions of the Earth's surface. Far more interesting than I originally thought
. The Maidenhead Locator System has more layers for more precise grid location, but for my use two layers are good starting point. In the future I want to test a logarithmically weighted based on proximity measurement, that might provide an even better understanding of location, this is based on the thought that the closer you are to an area of interest the more important that the location distance matters.
```python
#         ||                          |
# ***2*c  || ...   EN52wc    EN52xc   |   EN62ac    EN62bc     ...
# ***2*b  || ...   EN52wb    EN52xb   |   EN62ab    EN62bb     ...
# ***2*a  || ...   EN52wa    EN52xa   |   EN62aa    EN62ba     ...
# --------||--------------------------|----------------------------
# ***1*x  || ...   EN51wx    EN51xx   |   EN61ax    EN61bx     ...
# ***1*w  || ...   EN51ww    EN51xw   |   EN61aw    EN61bw     ...
# ***1*v  || ...   EN51wv    EN51xv   |   EN61av    EN61bv     ...
#         ||         ...       ...    |    ...       ...       ...
# -----------------------------------------------------------------
#         || ...   **5*w* -> **5*x*  ->   **6*a* -> **6*b*     ...
```
if your interested in your Maidenhead you can find it here: [Amateur Radio Ham Radio Maidenhead Grid Square Locator Map](https://www.levinecentral.com/ham/grid_square.php)
## lets code all the rules
My first approach was painfully inefficient - finding the southwest corner grid and then looping through all cells. 
```python
import math
#takes lat and long and finds the sw maidenhead using n, as the number of width/height
def maidenheadsw(lat, lon, n):
    num_maidenheads = (n*2+1)**2
    columns = math.sqrt(num_maidenheads)
    rows = math.sqrt(num_maidenheads)
      A = ord('A')
    # field
    field_lon = divmod(lon+180, 20)
    field_lat = divmod(lat+90, 10)
    field = chr(A+ int(field_lon[0])) + chr(A+int(field_lat[0]))
    # Square
    square_lon = divmod(field_lon[1] / 2, 1)
    square_lat = divmod(field_lat[1], 1)
    square = str(int(square_lon[0])) + str(int(square_lat[0]))
    # Subsquare
    subsquare_lon = divmod(square_lon[1]*24,1)
    subsquare_lat = divmod(square_lat[1]*24,1)
    subsquare = chr(A+int(subsquare_lon[0])).lower() + chr(A+int(subsquare_lat[0])).lower()

    # Maidenhead
    maidenhead = field + square + subsquare
    subsquare_lat_s = int(subsquare_lat[0]) - n
    #subsquare_lat_n = int(subsquare_lat[0]) + n
    subsquare_lon_w = int(subsquare_lon[0]) - n
    #subsquare_lon_e = int(subsquare_lon[0]) + n
    ss_lat_cycles = 0
    ss_lon_cycles = 0
    s_lat_cycles = 0
    s_lon_cycles = 0
    field_lat_s = int(field_lat[0])
    field_lon_w = int(field_lon[0])
    square_lat_s= int(square_lat[0])
    square_lon_w= int(square_lon[0])                  
    maiden_sw={}
    # subsquare_lat_s
    while subsquare_lat_s < 0:
        ss_lat_cycles += 1
        subsquare_lat_s += 24
    else:
        maiden_sw['subsquare_lat_s']=subsquare_lat_s
    # subsquare_lon_w
    while subsquare_lon_w < 0:
        ss_lon_cycles += 1
        subsquare_lon_w += 24
    else:
        maiden_sw['subsquare_lon_w']=subsquare_lon_w

   # square_lat_s
    while square_lat_s - ss_lat_cycles < 0:
        s_lat_cycles += 1
        square_lat_s  += 10
    else:
        maiden_sw['square_lat_s']= square_lat_s - ss_lat_cycles
    # square_lon_w
    while square_lon_w - ss_lon_cycles < 0:
        s_lon_cycles += 1
        square_lon_w  += 10
    else:
        maiden_sw['square_lon_w']= square_lon_w - ss_lon_cycles
    # field_lat_s
    while field_lat_s - s_lat_cycles < 0:
        field_lat_s += 18
    else:
        maiden_sw['field_lat_s']=field_lat_s - s_lat_cycles
   # field_lon_w
    while field_lon_w - s_lon_cycles < 0:
        field_lon_w += 18
    else:
        maiden_sw['field_lon_w']=field_lon_w - s_lon_cycles
          
    return maiden_sw#, columns


```

```python
maidenheadsw(31.308800,-86.393799, 25)

{'field_lat_s': 12,
 'field_lon_w': 4,
 'square_lat_s': 0,
 'square_lon_w': 5,
 'subsquare_lat_s': 6,
 'subsquare_lon_w': 18}
```

## That was Painful - Lets find another way

Around that same time I was taking a few fastAI courses ([Introduction to Machine Learning for Coders: Launch – fast.ai](https://www.fast.ai/posts/2018-09-26-ml-launch.html) , [Practical Deep Learning for Coders - Practical Deep Learning](https://course.fast.ai/)) Where Jeromy was talking about Broadcasting and how it was something that he always shared as a super power, so I though I would give that a try since it seemed to be applicable but before we start we need to look at some of the basics of Numpy and Broadcasting. 
### Numpy Basics

The np.arrange function by default returns a "rank one array"

```
x = np.arange(5); x.shape
>> (5,)
```
The problem is that rank one arrays don't work I would normally expect:

```
np.array_equal(x,x.T) 
>>True
```
That is because x and its transpose x.T have a shape of =  (5, )
To convert this to a vector you can use the .reshape() function. 

```
x = x.reshape((1,25)) # or x.reshape((1,len(x)))
x, x.shape
>>(array([[0, 1, 2, 3, 4]]), (1, 5))
```
-note* - x has double [[_]]'s now

To avoid using .reshape() all the time you could use np.nweaxis when creating the array
```
col_a= np.arange(cols)[np.newaxis]  # or np.arange(cols).reshape((5,1))
row_a= np.arange(rows)[:, np.newaxis]  # or np.arange(rows).reshape((1,5))

```
It might be a good habbit to add an assertation statement
```
assert(x.shape == (1,5))
```

### What is Broadcasting?
![Broadcasting](/public/images/broadcasting.png)

Broadcasting allows NumPy to perform operations on arrays of different shapes. Instead of writing explicit loops to manipulate each element individually, broadcasting automatically aligns arrays and performs element-wise operations, making code cleaner and significantly faster.

### The Broadcasting Solution

We are going to use Numpy to create a matrix of the adjustments to maidenhead, which will be used to create a list of maidenheads.

n is the number of cells/maidenheads on each side of the subject maidenhead. an n=2 would give us 2 on each side of the subject, or 25 cells/maidenheads in total.

With broadcasting, I could create two arrays representing latitude and longitude adjustments and apply them simultaneously. For a 5×5 grid of cells (radius 2 from center):
```
            *  *  *  *  *
            *  *  *  *  *
            *  *  S  *  *
            *  *  *  *  *
            *  *  *  *  *
``` 

```
#         ||                          |
# ***2*c  || ...   EN52wc    EN52xc   |   EN62ac    EN62bc     ...
# ***2*b  || ...   EN52wb    EN52xb   |   EN62ab    EN62bb     ...
# ***2*a  || ...   EN52wa    EN52xa   |   EN62aa    EN62ba     ...
# --------||--------------------------|----------------------------
# ***1*x  || ...   EN51wx    EN51xx   |   EN61ax    EN61bx     ...
# ***1*w  || ...   EN51ww    EN51xw   |   EN61aw    EN61bw     ...
# ***1*v  || ...   EN51wv    EN51xv   |   EN61av    EN61bv     ...
#         ||         ...       ...    |    ...       ...       ...
# -----------------------------------------------------------------
#         || ...   **5*w* -> **5*x*  ->   **6*a* -> **6*b*     ...
  
```
what we need to do is make two different arrays that can be used for the adjustments that need to be made.
we want to build two different arrays so that we can use broadcasting to get a list of all the maidenheads

```
array([[ 2,  2,  2,  2,  2],
       [ 1,  1,  1,  1,  1],
       [ 0,  0,  0,  0,  0],
       [-1, -1, -1, -1, -1],
       [-2, -2, -2, -2, -2]])
       
```
And
```
array([[-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2]])

```

### Set-up  : matrix or numpy.ndarray.
A Matrix is a special type of ndarray
```python
n=2
num_maidenheads = (n*2+1)**2
n_rows = n_cols = int(math.sqrt(num_maidenheads))
```
Create a n_row by n_cols array of all ones
```python
import numpy as np
x = np.ones((n_rows,n_cols), dtype=np.int);x, x.shape

(array([[1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1]]), (5, 5))
```
*Rows* and columns
```python
row_a= np.arange(n_rows)[np.newaxis] # or np.arange(row_a).reshape((1,5))
col_a= np.arange(n_cols)[:, np.newaxis] # or np.arange(col_a).reshape((5,1))
col_a, col_a.shape

(array([[0],
        [1],
        [2],
        [3],
        [4]]), (5, 1))
```


```python
cn = col_a[::-1]-n; cn      

#Equivalent to m[::-1,...]. Does not require the array to be two-dimensional
#The dots (...) represent as many colons as needed to produce a complete indexing tuple

array([[ 2],
       [ 1],
       [ 0],
       [-1],
       [-2]])
```

```python
lat_adj= cn * x; lat_adj

array([[ 2,  2,  2,  2,  2],
       [ 1,  1,  1,  1,  1],
       [ 0,  0,  0,  0,  0],
       [-1, -1, -1, -1, -1],
       [-2, -2, -2, -2, -2]])
```

```python
row_a, row_a.shape

(array([[0, 1, 2, 3, 4]]), (1, 5))
```

```python
rn= row_a -n; rn

array([[-2, -1,  0,  1,  2]])
```

```python
lon_adj= rn * x
lon_adj

array([[-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2],
       [-2, -1,  0,  1,  2]])
```


## Maidenheads function (parts)
```python
lat,lon = 31.308800,-86.393799
```
**Maidenhead** and cell pieces:
```python
A = ord('A')
a = divmod(lon+180, 20) #divmod(numerator,denominator) returns (quotient and remainder)
b = divmod(lat+90, 10)
a_field_lon = int(a[0])
a_field_lat = int(b[0])
#a_field = chr(A+ int(a[0])) + chr(A+int(b[0])) # a field
square_lon_dm = divmod(a[1] / 2, 1)
square_lat_dm = divmod(b[1], 1)
square_lon = int(square_lon_dm[0])
square_lat = int(square_lat_dm[0])
#square = str(int(square_lon_dm[0])) + str(int(square_lat_dm[0]))
subsquare_lon_dm = divmod(square_lon_dm[1]*24,1)
subsquare_lat_dm = divmod(square_lat_dm[1]*24,1)
subsquare_lon = int(subsquare_lon_dm[0])                
subsquare_lat = int(subsquare_lat_dm[0])

#subsquare = chr(A+int(subsquare_lon_dm[0])).lower() + chr(A+int(subsquare_lat_dm[0])).lower()

#  get cell
m_cell_lon = a_field_lon * 18 * 10 * 24 +  square_lon * 10 *24 + subsquare_lon
m_cell_lat = a_field_lat * 18 * 10 * 24 +  square_lat * 10 *24 + subsquare_lat
```
Broadcasting allows you to add the subject cell value to the latitude and longitude adjustment 2-d array
```python
lat_array = lat_adj + m_cell_lat
lon_array = lon_adj + m_cell_lon
lat_array, lon_array

(array([[52089, 52089, 52089, 52089, 52089],
        [52088, 52088, 52088, 52088, 52088],
        [52087, 52087, 52087, 52087, 52087],
        [52086, 52086, 52086, 52086, 52086],
        [52085, 52085, 52085, 52085, 52085]]),
 array([[18737, 18738, 18739, 18740, 18741],
        [18737, 18738, 18739, 18740, 18741],
        [18737, 18738, 18739, 18740, 18741],
        [18737, 18738, 18739, 18740, 18741],
        [18737, 18738, 18739, 18740, 18741]]))
```
We have already created a fuction(cell2maidenhead) that can convert a cell to a maidenhead now we need to be able to apply it to the array of cells that we have created by using the np.vectorize function. From my understanding this still uses a loop so we might want to refactor this function.

```python
np_cell2maidenhead = np.vectorize(cell2maidenhead)
np_maids = np_cell2maidenhead(lat_array,lon_array); np_maids

array([['EM61rj', 'EM61sj', 'EM61tj', 'EM61uj', 'EM61vj'],
       ['EM61ri', 'EM61si', 'EM61ti', 'EM61ui', 'EM61vi'],
       ['EM61rh', 'EM61sh', 'EM61th', 'EM61uh', 'EM61vh'],
       ['EM61rg', 'EM61sg', 'EM61tg', 'EM61ug', 'EM61vg'],
       ['EM61rf', 'EM61sf', 'EM61tf', 'EM61uf', 'EM61vf']], dtype='<U6')
```
Great it looks like we have the maidenheads that we want, now we need to convert them to a list. we can use the np.tolist() to convert to a list.
```python
l = np_maids.tolist(); l

[['EM61rj', 'EM61sj', 'EM61tj', 'EM61uj', 'EM61vj'],
 ['EM61ri', 'EM61si', 'EM61ti', 'EM61ui', 'EM61vi'],
 ['EM61rh', 'EM61sh', 'EM61th', 'EM61uh', 'EM61vh'],
 ['EM61rg', 'EM61sg', 'EM61tg', 'EM61ug', 'EM61vg'],
 ['EM61rf', 'EM61sf', 'EM61tf', 'EM61uf', 'EM61vf']]
```
The tolist() function returned a list but it is a nested list(list of lists), look at the extra square brackets, so we are going to have to flatten it. I choose to flatten before the cell2maidenhead function. We can flatten it with the np.flatten() function.

```python
f_lat = lat_array.flatten()
f_lon = lon_array.flatten()
f_lat, f_lon

(array([52089, 52089, 52089, 52089, 52089, 52088, 52088, 52088, 52088,
        52088, 52087, 52087, 52087, 52087, 52087, 52086, 52086, 52086,
        52086, 52086, 52085, 52085, 52085, 52085, 52085]),
 array([18737, 18738, 18739, 18740, 18741, 18737, 18738, 18739, 18740,
        18741, 18737, 18738, 18739, 18740, 18741, 18737, 18738, 18739,
        18740, 18741, 18737, 18738, 18739, 18740, 18741]))
```
Convert cells to maidenheads with flattened arrays
```python
maidenhead_array = np_cell2maidenhead(f_lat,f_lon)
```
Convert flattened maidenhead array to list
```python
maidenhead_list = maidenhead_array.tolist()
maidenhead_list

['EM61rj', 'EM61sj', 'EM61tj', 'EM61uj', 'EM61vj', 'EM61ri', 'EM61si', 'EM61ti', 'EM61ui', 'EM61vi', 'EM61rh', 'EM61sh', 'EM61th', 'EM61uh', 'EM61vh', 'EM61rg', 'EM61sg', 'EM61tg', 'EM61ug', 'EM61vg', 'EM61rf', 'EM61sf', 'EM61tf', 'EM61uf', 'EM61vf']
```



## Putting It All Together

The final solution involved three main components:

1. **Convert coordinates to an integer-based cell representation** for easier calculations:

```python
def cell2maidenhead(lat_cell, lon_cell):
    A = ord('A')
    lon_f=divmod(lon_cell,24*10*18)
    lon_s= divmod(lon_f[1],10*24)
    lat_f=divmod(lat_cell,24*10*18)
    lat_s= divmod(lat_f[1],10*24)
    a_field = chr(A+int(lon_f[0])) + chr(A+int( lat_f[0]))
    square = str(int(lon_s[0])) + str(int(lat_s[0]))
    subsquare = chr(A+int(lon_s[1])).lower() + chr(A+int(lat_s[1])).lower()
    maidenhead = a_field + square + subsquare
    return maidenhead
```

2. **Apply broadcasting to generate all surrounding cells**:

```python
def maidenheads(lat, lon, n=0):
    num_maidenheads = (n*2+1)**2
    n_rows = n_cols = int(math.sqrt(num_maidenheads))
    #  setup arrays
    x = np.ones((n_rows,n_cols), dtype=np.int)
    row_a= np.arange(n_rows)[np.newaxis]
    col_a= np.arange(n_cols)[:, np.newaxis]
    cn=col_a[::-1]-n
    lat_adj = cn * x
    rn= row_a - n
    lon_adj = rn * x
    #  get subject maidenhead from lat,lon
    A = ord('A')
    a = divmod(lon+180, 20) #divmod(numerator,denominator) returns (quotient and remainder)
    b = divmod(lat+90, 10)
    a_field_lon = int(a[0])
    a_field_lat = int(b[0])
    # a_field = chr(A+ int(a[0])) + chr(A+int(b[0])) # a field
    square_lon_dm = divmod(a[1] / 2, 1)
    square_lat_dm = divmod(b[1], 1)
    square_lon = int(square_lon_dm[0])
    square_lat = int(square_lat_dm[0])
    # square = str(int(square_lon_dm[0])) + str(int(square_lat_dm[0]))
    subsquare_lon_dm = divmod(square_lon_dm[1]*24,1)
    subsquare_lat_dm = divmod(square_lat_dm[1]*24,1)
    subsquare_lon = int(subsquare_lon_dm[0])                
    subsquare_lat = int(subsquare_lat_dm[0])
    # subsquare = chr(A+int(subsquare_lon_dm[0])).lower() + chr(A+int(subsquare_lat_dm[0])).lower()
    #  get cell
    m_cell_lon = a_field_lon * 18 * 10 * 24 +  square_lon * 10 *24 + subsquare_lon
    m_cell_lat = a_field_lat * 18 * 10 * 24 +  square_lat * 10 *24 + subsquare_lat
    # cell arrays
    lat_array= m_cell_lat + lat_adj
    lon_array= m_cell_lon + lon_adj
    #flatten
    f_lat = lat_array.flatten()
    f_lon = lon_array.flatten()
    #convert to maidenhead
    np_cell2maidenhead = np.vectorize(cell2maidenhead)    
    maidenhead_array = np_cell2maidenhead(f_lat,f_lon)
    #convert maidenheads to list
    maidenhead_list = maidenhead_array.tolist()
    return maidenhead_list
```

```python
t = maidenheads(31.308800,-86.393799,2)
t
['EM61rj', 'EM61sj', 'EM61tj', 'EM61uj', 'EM61vj', 'EM61ri', 'EM61si', 'EM61ti', 'EM61ui', 'EM61vi', 'EM61rh', 'EM61sh', 'EM61th', 'EM61uh', 'EM61vh', 'EM61rg', 'EM61sg', 'EM61tg', 'EM61ug', 'EM61vg', 'EM61rf', 'EM61sf', 'EM61tf', 'EM61uf', 'EM61vf']
```

apply it to the whole dataframe
```python
n=2
df['maidenheads'] = df.apply(lambda x: maidenheads(lat=x['latitude_deg'], lon= x['longitude_deg'], n=n), axis=1)
```

The beauty of this approach lies in its elegance. Instead of nested loops or complex logic, broadcasting lets me perform operations on entire arrays at once.
### Why This Matters

Broadcasting is a game-changer this technique:

2. **Improves code readability** - no explicit loops means cleaner code
3. **Increases performance** - vectorized operations are much faster
4. **Reduces memory usage** - broadcasting doesn't create unnecessary copies

For my geospatial problem, broadcasting transformed a tedious process into an elegant solution that could scale to any size grid.

## Conclusion: From Airports to Algorithms

What started in 2019 as a simple quest to analyze airport proximity transformed into a journey of discovery with NumPy's broadcasting capabilities. Once I had my `maidenheads()` function working, I could apply it to my entire dataset of airports:

```python
# Add maidenhead locator to each airport 
df['maidenhead'] = df.apply( lambda x: maidenhead(lat=x['latitude_deg'], lon=x['longitude_deg']), axis=1 ) 
# Add surrounding maidenheads (5x5 grid) for each airport 
n = 2 
# Radius of 2 gives a 5x5 grid 
df['maidenheads'] = df.apply( lambda x: maidenheads(lat=x['latitude_deg'], lon=x['longitude_deg'], n=n), axis=1 ) 
```

This approach enabled me to efficiently analyze proximity relationships between airports and their surrounding areas, opening up possibilities for more sophisticated geospatial analysis.

Broadcasting isn't just a technical trick it's a different way of thinking about array operations that can simplify complex problems. It transformed a tedious process into an elegant solution that could scale to any size grid.

What I initially thought would be a simple task ("oh boy was I wrong," as I noted in my original code comments) became the starting point for my geospatial journey. It forced me to learn much more about geospatial data and helped me understand and use broadcasting, an amazing tool when dealing with tensors of different sizes.

Next time you find yourself writing nested loops to manipulate arrays, consider whether broadcasting might offer a more elegant solution. Sometimes the most interesting coding journeys begin with what seems like a simple problem.