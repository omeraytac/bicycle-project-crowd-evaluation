import json
import matplotlib.pyplot as plt
import pprint

## returns the number of annotators in param=annotations
# param type: json
# return type: integer
def number_of_annotators(annotations):
	tasks = annotations["results"]["root_node"]["results"]
	annotators = set()
	for task_id in tasks:
		for result in tasks[task_id]["results"]:
			annotators.add(result["user"]["id"])
	return len(annotators)

## returns the number of annotations for every annotators in param=annotations
# param type: json
# return type: dictionary
def annotation_times(annotations):
	tasks = annotations["results"]["root_node"]["results"]
	annotators = {}
	for task_id in tasks:
		for result in tasks[task_id]["results"]:
			if result["user"]["id"] in annotators:
				annotators[result["user"]["id"]] += 1
			else:
				annotators[result["user"]["id"]] = 1
	return annotators

## returns whether the all annotators produced the same amount of results or not in param=annotators.
# param type: json
# return type: string
def is_all_same(annotations):
	occur = annotation_times(annotations)
	occur_set = set(occur)
	if len(occur) == 1:
		return "All annotators produced the same amount of results."
	else:
		return "All annotators did not produce the same amount of results."

## returns the number of answers "yes" or "no" for every images in param=annotations
# param type: json
# return type: dictionary
def answers_for_images(annotations):
	tasks = annotations["results"]["root_node"]["results"]
	images = {}
	for task_id in tasks:
		for result in tasks[task_id]["results"]:
			if not result["task_input"]["image_url"] in images:
				images[result["task_input"]["image_url"]] = {"yes": 0, "no": 0, "diff": 0}
			if result["task_output"]["answer"] == "no":
				images[result["task_input"]["image_url"]]["no"] += 1
			else:
				images[result["task_input"]["image_url"]]["yes"] += 1
			images[result["task_input"]["image_url"]]["diff"] = abs(images[result["task_input"]["image_url"]]["no"]-images[result["task_input"]["image_url"]]["yes"])
	return images

## returns the most disagreed image in param=annotations
# param type: json
# return type: string, dictionary
def biggest_disagreement(annotations):
	images = answers_for_images(annotations)
	min_diff = 11
	out_image = ""
	for image in images:
		if images[image]["diff"] < min_diff:
			min_diff = images[image]["diff"]
			out_image = image
	return out_image, images[out_image]


## returns the number of results "can't solve" and "corrupt data" for every annotators in param=annotations
# param type: json
# return type: dictionary
def other_results_of_users(annotations):
	tasks = annotations["results"]["root_node"]["results"]
	annotators = {}
	for task_id in tasks:
		for result in tasks[task_id]["results"]:
			if not result["user"]["id"] in annotators:
				annotators[result["user"]["id"]] = {"occurrence": 0, "cant_solve": 0, "corrupt_data": 0}
			annotators[result["user"]["id"]]["occurrence"] += 1
			if result["task_output"]["cant_solve"]:
				#print("cant_solve: ", result["task_input"]["image_url"])
				annotators[result["user"]["id"]]["cant_solve"] += 1
			elif result["task_output"]["corrupt_data"]:
				#print("corrupt_data: ", result["task_input"]["image_url"])
				annotators[result["user"]["id"]]["corrupt_data"] += 1
	return annotators

def balance_of_reference(references):
	yes = 0
	no = 0
	for image in references:
		if references[image]["is_bicycle"]:
			yes += 1
		else:
			no += 1
	return yes, no

def confusion_matrix(annotations, references):
	tasks = annotations["results"]["root_node"]["results"]
	annotators = {}
	for task_id in tasks:
		for result in tasks[task_id]["results"]:
			image_url = result["task_input"]["image_url"]
			image = image_url[-12:-4]
			if not result["user"]["id"] in annotators:
				annotators[result["user"]["id"]] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
			if result["task_output"]["answer"] == "yes" and references[image]["is_bicycle"] :
				annotators[result["user"]["id"]]["tp"] += 1
			elif result["task_output"]["answer"] == "yes" and not references[image]["is_bicycle"]:
				annotators[result["user"]["id"]]["fp"] += 1
			elif result["task_output"]["answer"] == "no" and references[image]["is_bicycle"]:
				annotators[result["user"]["id"]]["fn"] += 1
			elif result["task_output"]["answer"] == "no" and not references[image]["is_bicycle"]:
				annotators[result["user"]["id"]]["tn"] += 1
	return annotators
				
def accuracy(matrix):
	accuracy_dict = {}
	for user in matrix:
		accuracy_dict[user] = (matrix[user]["tp"] + matrix[user]["tn"])/(matrix[user]["tp"] + matrix[user]["tn"] + matrix[user]["fp"] + matrix[user]["fn"])
	return accuracy_dict

def f_score(matrix):
	f_score_dict = {}
	for user in matrix:
		f_score_dict[user] = matrix[user]["tp"]/(matrix[user]["tp"] + (1/2)*(matrix[user]["fp"] + matrix[user]["fn"]))
	return f_score_dict

## void function that plots the data and saves it as .png 
def plot_save(data, xlabel, ylabel, title, x_rotation=0, y_rotation=0, fig=0):
	plt.figure(fig)
	plt.bar(*zip(*data.items()))
	plt.ylabel(ylabel)
	plt.xlabel(xlabel)
	plt.xticks(rotation=x_rotation)
	plt.title(title)
	plt.plot(1)
	plt.savefig("./" + title + ".png")


def main():
	with open("./anonymized_project.json") as anon:
		annotations = json.load(anon)

	# 1-a
	a1 = number_of_annotators(annotations)
	print("Number of annotators: ", a1)

	# 1-b
	b1 = annotation_times(annotations)
	plot_save(b1, "User ids", "annotation times", "Number of annotations", x_rotation=90, fig=0)

	number_of_annotations = list(b1.values())
	print("Min annotation time: ", min(number_of_annotations))
	print("Max annotation time: ",max(number_of_annotations))
	print("Average annotation time: ",sum(number_of_annotations)/len(number_of_annotations))

	# 1-c
	isAllSame = is_all_same(annotations)
	print(isAllSame)

	# 1-d
	disagreed_image, disagreed_image_values = biggest_disagreement(annotations)
	print("The most disagreed image:", disagreed_image[-12:-4], "where number of yes:", disagreed_image_values["yes"], "and number of no:", disagreed_image_values["no"])

	# 2-a
	others_of_users = other_results_of_users(annotations)
	pp = pprint.PrettyPrinter()
	pp.pprint(others_of_users)

	# 3
	with open("./references.json") as anon:
		references = json.load(anon)
	images = answers_for_images(annotations)
	yes, no = balance_of_reference(references)
	print("Number of yes", yes, "and number of no", no, "Since the outputs are very close, we can say that this dataset is pretty balanced.")

	# 4
	conf_matrix = confusion_matrix(annotations,references)
	f_scores = f_score(conf_matrix)
	accuracies = accuracy(conf_matrix)
	plot_save(f_scores, "User ids", "F Scores", "F Score Chart", x_rotation=90, fig=1)
	plot_save(accuracies, "User ids", "Accurracies", "Accuracy Chart", x_rotation=90, fig=2)

if __name__ == "__main__":
	main()