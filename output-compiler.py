# Compiles disparate output files into a single file for easier analysis
from pathlib import Path

def main():
    input_dir = "{}\\results".format(Path.cwd())
    output_file = "{}\\compiled_results.txt".format(Path.cwd())
    with open(output_file, "w") as output:
        total_urls = 0
        total_unblocked = 0
        for filepath in Path(input_dir).glob("*.txt"):
            with open(filepath, "r") as file:
                lines = file.readlines()
                total_urls += int(lines[3].split(" ")[3])
                total_unblocked += int(lines[4].split(" ")[2])
        
        print("Total URLs: {}".format(total_urls), file=output)
        print("Total Unblocked: {}".format(total_unblocked), file=output)
        print("Unblocked Percentage: {:.2f}%".format((total_unblocked / total_urls) * 100), file=output)
    
    output.close()


if __name__ == "__main__":
    main()