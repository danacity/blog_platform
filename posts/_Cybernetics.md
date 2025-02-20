---
title: Cybernetics - Building Compound AI Systems
date: 2025-02-19
draft: true
excerpt: 'Norbert Wiener coined the term Cybernetics in his 1950s book "The Human Use of Human Beings: Cybernetics and Society'
tags:
  - FastHTML
Diataxis:
  - Narrative
---

## Show your work

how do 

Error analysis - where your system goes wrong
- classify and count the errors - spend time on most impactful errors 
-  clarifies 
	- what you should do next
- error analysis areas
	- looking at data, and notes
	- data analysis - systematic patterns 
- if you don't have ground truth, what are you measuring
- you don't know what you are looking for until you start looking at your data
	- spreadsheet 
		- URL, article text(uput into LLM), summary(llm output), failure mode
		- take notes on what went wrong
			- off topic
			- context relevance, answer faithfulness, answer relevance
			- start with just notes, then binary 
		- going thought data will help you identify what matters to you. 
- what if you dont have data

- dimensions or facets of your data, things to help you identify how it matters to your application. 
	- article type, question type, subject, code, source document, source, 
	- enrich your data so you can analyze it. 
- after error analysis you can write test to stress test specific identified errors
	- data issue in function calling 
	- braintrust
		- prompt 
			- input
			- expected output
		- braintrust has scoring function
	- langsmith - has a data viewer that helps you label data quicker
		- has hotkeys
		- write notes
	- argilla
		- ?
	- phenix 
		- open sourced 
	- Honeycome
		- has query language - has translation tool that convert human promt to honeycome query language
	- build your own
		- create it fast, just do something
		- why is it good or bad
		- 