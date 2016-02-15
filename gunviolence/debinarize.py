import argparse
import csv
import matplotlib.pyplot as plt
import pandas
import sklearn.decomposition

CONVERSIONS = {
    "Playing with gun": "Idiocy, not aggression",
    "Bar/club incident - in or around establishment": "",
    "Suicide": "Suicide or suicide attempt",
    "Child with gun - no shots fired": "Child involvement",
    "Defensive Use - WITHOUT a gun": "Defensive use",
    "Concealed Carry License - Perpetrator": "",
    "Child injured (not child shooter)": "Child involvement",
    "Accidental Shooting at a Business": "Accidental shooting",
    "Mistaken ID  (thought it was an intruder/threat, was friend/family)": "Mistaken ID",
    "Gun range/gun shop/gun show shooting": "",
    "Suicide - Attempt": "Suicide or suicide attempt",
    "School Shooting - elementary/secondary school": "School incident",
    "Defensive Use - Stand Your Ground/Castle Doctrine established": "Defensive use",
    "Shots fired, no action (reported, no evidence found)": "",
    "Officer Involved Shooting - Officer shot": "Officer involvement",
    "Defensive Use - Shots fired, no injury/death": "Defensive use",
    "Officer Involved Shooting - Perpetrator suicide at standoff": "Officer involvement",
    "Child Involved Incident": "Child involvement",
    "Accidental Shooting - Death": "Accidental shooting",
    "Pistol-whipping": "Pistol-whipping",
    "Concealed Carry License - Victim": "",
    "Defensive Use - Victim stops crime": "Defensive use",
    "Officer Involved Shooting - Perpetrator killed": "Officer involvement",
    "School Shooting - university/college": "School incident",
    "Kidnapping/abductions/hostage": "Kidnapping",
    "Criminal act with stolen gun": "Stolen gun involvement",
    "Domestic Violence": "Domestic violence",
    "Defensive Use - Crime occurs, victim shoots perpetrator": "Defensive use",
    "BB/pellet gun": "BB/pellet gun",
    "Home Invasion - Resident injured": "Home invasion",
    "Officer Involved Shooting - Shots fired, no injury": "Officer involvement",
    "IDIOCY, NOT AGGRESSION": "Idiocy, not aggression",
    "Defensive Use": "Defensive use",
    "Self-Inflicted (not suicide or suicide attempt - NO PERP)": "Self-inflicted",
    "Home Invasion - No death or injury": "Home invasion",
    "Gun at school, no death/injury - elementary/secondary school": "School incident",
    "Institution/Group/Business": "",
    "Accidental Shooting - Injury": "Accidental shooting",
    "LOCKDOWN/ALERT ONLY:  No GV Incident Occurred Onsite": "Lockdown alert",
    "Gang involvement": "Gang involvement",
    "Stolen/Illegally owned gun{s} recovered during arrest/warrant": "Stolen gun involvement",
    "Gun(s) stolen from owner": "Stolen gun involvement",
    "Under the influence of alcohol or drugs (only applies to the perpetrator)": "Perpetrator under influence",
    "Officer Involved Shooting - Perpetrator surrender at standoff": "Officer involvement",
    "Accidental/Negligent Discharge": "Accidental shooting",
    "Home Invasion": "Home invasion",
    "ATF/LE Confiscation/Raid/Arrest": "ATF/LE confiscation",
    "School Incident": "School incident",
    "Officer Involved Incident - Weapon involved but no shots fired": "Officer involvement",
    "Officer Involved Shooting - Perpetrator shot": "Officer involvement",
    "Car-jacking": "Car-jacking",
    "Accidental Shooting": "Accidental shooting",
    "Armed robbery with injury/death and/or evidence of DGU found": "Armed robbery",
    "Drug involvement": "Drug involvement",
    "Brandishing/flourishing/open carry/lost/found": "Brandishing, open carry, or lost and found",
    "Possession of gun by felon or prohibited person": "Possession of gun by felon or prohibited person",
    "Drive-by (car to street, car to car)": "Drive-by",
    "Officer Involved Incident": "Officer involvement",
    "Possession (gun(s) found during commission of other crimes)": "Gun found during commission of other crime",
    "Shots Fired - No Injuries": "No injuries",
    "Non-Shooting Incident": "No shooting",
    "Shot - Dead (murder, accidental, suicide)": "Death involvement",
    "Shot - Wounded/Injured": "Injury involvement",
}

def get_columns(csvfile):
    oldcols = []
    newcols = []
    reader = csv.DictReader(csvfile)
    for row in reader:
        oldcols = [r for r in row.iterkeys()]
        break
    for col in oldcols:
        if col not in CONVERSIONS:
            newcols.append(col)
        elif CONVERSIONS[col] == "":
            continue
        else:
            newcols.append(CONVERSIONS[col])
    return oldcols, list(set(newcols))

def convert(infilename, outfilename):
    with open(infilename) as input, open(outfilename, "w") as output:
        oldcols, newcols = get_columns(input)
        input.seek(0)
        reader = csv.DictReader(input)
        writer = csv.DictWriter(output, newcols)
        writer.writeheader()
        for row in reader:
            newrow = {}
            for (oldkey, oldval) in row.iteritems():
                if oldkey not in CONVERSIONS:
                    newrow[oldkey] = oldval
                elif CONVERSIONS[oldkey] == "":
                    continue
                else:
                    newval = False
                    oldval = True if oldval == "True" else False
                    if CONVERSIONS[oldkey] in newrow:
                        newval = newrow[CONVERSIONS[oldkey]]
                    newrow[CONVERSIONS[oldkey]] = newval or oldval
            writer.writerow(newrow)

def get_binary_column_keys(csvfile):
    binary_columns = []
    reader = csv.DictReader(csvfile)
    for row in reader:
        for (key, val) in row.iteritems():
            if val == "True" or val == "False":
                binary_columns.append(key)
        break
    return binary_columns

def explore(infilename, outfilename):
    nominals = []
    num_trues = []
    vectors = []
    with open(infilename) as input, open(outfilename, "w") as output:
        binary_columns = get_binary_column_keys(input)
        input.seek(0)
        reader = csv.DictReader(input)
        for row in reader:
            binary_vals = [True if row[c] == "True" else False for c in binary_columns]
            binary_nums = [int(v) for v in binary_vals]
            vectors.append(binary_nums)
            binary_string = "".join([str(n) for n in binary_nums])
            nominals.append(binary_string)
            num_trues.append(sum(binary_nums))
    print "num nominal", len(set(nominals))
    print "max num trues", max(num_trues)
    grouped = zip(nominals, num_trues)
    grouped.sort(key=lambda x: x[1], reverse=True)
    #for item in grouped:
    #    print item
    num_trues.sort(reverse=True)
    plt.plot(range(len(num_trues)), num_trues)
    plt.savefig("num-trues-dist.pdf")

    df = pandas.DataFrame(vectors, columns=binary_columns)
    #row_counts = df.sum(1)
    #row_counts.sort(ascending=False)
    #plt.plot(range(len(num_trues)), row_counts)
    #plt.show()
    col_counts = df.sum()
    col_counts.sort()
    pandas.set_option("display.max_rows", 100)
    print col_counts
    col_counts.sort(ascending=False)
    #plt.plot(range(len(binary_columns)), col_counts)
    #plt.show()

    #print df.head()
    #pca = sklearn.decomposition.PCA(n_components=5)
    #pca.fit(df)
    #print pca.components_

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Convert binary columns to nominal.")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    explore(args.input, args.output)
    
