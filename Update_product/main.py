import sys
from selenium.webdriver import FirefoxOptions
from selenium import webdriver
from helium import * # Helium is a higher level webdriver that still allows for use of selenium webdriver
import logging
import logging.config
from concurrent.futures import ThreadPoolExecutor
import os
import time
from Pages.login import Login # use to login Must be first to be called
from Pages.Variants import Variants # uses local one

sys.path += ['\\\\work\\tech\\henry\\programs\\python\\bgt-automate\\create_product'] # adds to path
# Use/import methods from other directories https://www.reddit.com/r/learnpython/comments/q850ll/eli5_why_i_cant_import_from_another_director_and/hgn06xs/?context=3
from credentials import Credentials
from locators import Locators
from driver_setup import DriverSetup
from file_handler import FileHandler

all_products_list = [50, 53, 59, 60, 61, 62, 65, 70, 71, 78, 79, 80, 81, 153, 163, 187, 209, 253, 292, 304, 312, 319, 342, 380, 381, 387, 389, 390, 414, 435, 444, 455, 473, 474, 475, 476, 478, 479, 483, 528, 
529, 552, 562, 565, 572, 576, 582, 586, 588, 594, 604, 620, 621, 623, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 694, 695, 696, 697, 700, 701, 702, 703, 704, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 740, 741, 742, 743, 744, 745, 746, 747, 749, 750, 751, 752, 753, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 838, 839, 840, 841, 842, 843, 855, 856, 857, 859, 860, 861, 863, 864, 865, 866, 867, 868, 869, 870, 872, 873, 874, 875, 876, 877, 
878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1067, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1099, 1100, 1103, 1104, 1105, 1106, 1107, 1191, 1192, 1194, 1195, 1196, 1197, 1198, 1199, 1201, 1202, 1211, 1227, 1228, 1230, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1684, 1685, 1686, 1687, 1688, 1689, 1690, 1691, 1692, 1693, 1694, 1695, 1696, 1697, 1698, 2058, 2059, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2110, 2111, 2112, 2113, 2115, 2116, 2117, 2118, 2119, 2120, 2121, 2122, 2123, 2124, 2125, 2126, 2127, 2128, 2130, 2136, 2207, 2208, 2209, 2210, 2212, 2213, 2214, 2215, 2216, 2217, 2218, 2219, 2220, 2221, 2222, 2223, 2225, 2226, 2227, 2228, 2229, 2230, 2231, 2232, 2233, 2234, 2239, 2240, 2241, 2244, 2245, 2247, 2248, 2249, 2250, 2251, 2252, 2253, 2257, 2259, 2268, 2269, 2271, 2272, 2278, 2279, 2280, 2281, 2282, 2285, 2295, 2296, 2297, 2298, 2314, 2315, 2320, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2333, 2334, 2335, 2336, 2337, 2338, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2361, 2377, 2378, 2379, 2380, 2382, 2383, 2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391, 2392, 2393, 2394, 2398, 2399, 2400, 2401, 2402, 2403, 2408, 2409, 2410, 2411, 2412, 2413, 2414, 2415, 2416, 2417, 2418, 2419, 2420, 2421, 2429, 2430, 2431, 2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441, 2444, 2445, 2446, 2447, 2448, 2449, 2450, 2451, 2452, 2453, 2454, 2455, 2456, 2458, 2459, 2461, 2462, 2515, 2530, 2531, 2532, 2534, 2537, 2538, 2540, 2541, 2542, 2543, 2544, 2546, 2547, 2548, 2556, 2557, 2562, 2564, 2565, 2566, 2567, 2570, 2572, 2576, 2577, 2578, 2618, 2619, 2621]


"""
Set up logger, the config for this logger can be found in loggin_config.json which should be in this folder
    there are several options for the logger including sending SMTP emails once a status of WARN or greater has been met, to change the
    email and the layout of the log, just make changes to the config
"""
logging.config.dictConfig(FileHandler(f'\\\\work\\tech\\henry\\programs\\python\\bgt-automate\\update_product\\loggin_config.json').open_json())
logger = logging.getLogger(__name__)

drivers = [DriverSetup(f'https://backgroundtown.com/Admin/ProductVariant/Edit/{str(i)}', headless=False)._get_driver() for i in all_products_list]

with ThreadPoolExecutor(max_workers=None) as executor: # will used the max amount of thread available to the computer, use `max_workers= `to change this
    """
    https://rednafi.github.io/digressions/python/2020/04/21/python-concurrent-futures.html
    map() requires a function followed by parameters which has to be an iterable, like an `array`
    """
    start_time = time.perf_counter()
    executor.map(Login().login, drivers) # log in on all available windows
    elapsed_time = time.perf_counter() - start_time
    print(f"Elapsed time for driver creation an Login: {elapsed_time:0.4f} seconds")
    executor.map(Variants().sort_sizes, drivers) # hopefully can work after
    [driver.quit() for driver in drivers]