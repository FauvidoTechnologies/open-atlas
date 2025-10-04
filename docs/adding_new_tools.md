Adding new tools is an extremely easy process:

1. Go to `oatlas/tools`
2. Create a new directory, say `new_tool_x/`
3. Make files or directories as you need. In the files make sure to follow the following syntax

```py
class ClassName:
	@staticmethod
	def some_important_function_1(arguments):
		# Do something
		return

	@staticmethod
	def some_important_function_2(arguments):
		# Do something
		return
```

> Ensure that the class name ends with `Engine`

4. Now head over to `oatlas/core/lib/classes.py`. Add an entry for the class there as a function to Gemini. Define the definition inside `ClassTools`
5. Now head over to `oatlas/core/lib/functions.py`. Add an entry for the class there and the functions defined inside the class. Make sure to add the class correctly inside `class_function_dict`.
6. Edit the `oatlas/tools/__init__.py` file and import the engine name there.
7. Now head over to `oatlas/core/registry.py`. Import the `ClassName` from the `__init__.py` file and add the `ClassName` to `all_classes`.
8. Update the `oatlas/methods/methods.yaml` file as well with whatever you have added.
9. Create description for your functions over at `oatlas/utils/tool_descriptions`