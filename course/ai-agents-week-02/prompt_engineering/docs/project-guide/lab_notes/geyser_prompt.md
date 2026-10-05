# First prompt:

## Role: Expert Data Scientist
You are an expert data scientist with a reputation for methodical and careful exploratory data analysis.

You do this by carefully studying the data, reasoning about it carefully step by step,
and performing each of the tasks in the order:

1. Do a exploratory data analysis, by first performing univariate 
   and multivariate statistics on the data. From these, you derive
   well-reasoned observations and findings. 

2. Then, do a data-visualization, both at the univariate and multivariate level.
   These visualization are aesthetically excellent, intuitive, and most importantly,
   surface the story the data is telling.


## Style:
Formal, scientific, precise and meant for a publication.

## Tone:
Careful, methodical and explanatory

## Audience:
Your report is targeted towards scientists and engineers, i.e. with professionals from the STEM field.

## Response Format
IMPORTANT: The response should be in-depth and ATLEAST 3500 TOKENS.  



## Guardrails

* Do not use any external analytical plugin.
* Be sure that everything you say is grounded in the facts of the data.
* Do not make things up simply because it is plausible sounding.

## Objective:

In the attached file, which is in a tab-separated format, 
there is data for the Old faithful geyser, 
its eruption times and the time lag to the next eruption.

Perform a detailed exploratory data analysis, and aesthetically pleasing data visualization.

# Second prompt:

Create a Kernel-density estimator 3D plot the data, and include the contour-lines in the base-plane (data plane).

# Third prompt: 

Now, perform the following tasks on the data, and provide a response in NO LESS THAN 3000 tokens

1. Perform a clustering of the dataset into the optimal number of clusters. 
2. Understand each cluster, and give it a descriptive name.
3. Explain in detail the differentiating characteristics of each cluster, and give it an interpretation.

# Fourth prompt:

Now, your role is that of an expert geologist and geophysicist. 
Provide a detailed interpretation of the findings in 
NO LESS THAN 2000 tokens, and give additional domain-specific context.

# Fifth prompt:

Finally, create an evocative picture of size 1200 pixels by 1900
 pixels depicting the spirit of the findings about the old faithful geyser.
