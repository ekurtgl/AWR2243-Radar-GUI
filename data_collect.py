from RDC_extract_2243 import RDC_extract_2243
from RDC_to_microDoppler_2243 import RDC_microDoppler
from RDC_to_rangeDOA_2243 import RDC_to_DOA_2243

main = '/media/emre/Windows-SSD/Users/emrek/Desktop/Technical/77ghz/data/'
fname = 'hand_updown_Raw_0.bin'
# main = '/home/emre/PycharmProjects/RadarGUI/data/'
# fname = '2022_03_15_13_30_44_subj_TEST_classTEST_Raw_0.bin'
fin = main + fname
out = '/home/emre/PycharmProjects/RadarGUI/data/'
fout = out + fname

RDC, params = RDC_extract_2243(fin)
# RDC_microDoppler(RDC, fout, params)
RDC_to_DOA_2243(RDC, fout, params, elev_or_azimuth='el', K=1, M=176, MTI=True)

