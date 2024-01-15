# atrial fibrillation ECG records

import wfdb.processing

# load MIT BIH AFib data & annotations
afib_record_ids = [
#     '00735', '03665', 
    '04015', '04043', '04048', '04126', 
    '04746', '04908', '04936', '05091', '05121', '05261', 
    '06426', '06453', '06995', '07162', '07859', '07879', 
    '07910', '08215', '08219', '08378', '08405', '08434', 
    '08455']

num_samps = 10800

afib_pieces = []
afib_ann_pieces = []
afib_afib_pieces = []
afib_normal_pieces = []
afib_other_pieces = []
afib_afib_and_other_pieces = []

for rec_id in afib_record_ids:
    # read rec and ann
    rec = wfdb.rdrecord('mit-bih-atrial-fibrillation-database-1.0.0/'+rec_id)
    ann = wfdb.rdann('mit-bih-atrial-fibrillation-database-1.0.0/'+rec_id, extension='atr')
    # resample rec and ann to 360 Hz
    afib_resampled, afib_annotation_resampled = wfdb.processing.resample_multichan(rec.__dict__['p_signal'], ann, 250, 360)
    ann_samples = [int(round(i*360.0/250.0)) for i in ann.__dict__['sample']]
    start = 0
    end = num_samps
    start_ann = None
    while end <= 12960000:
        # cut out the 30 second piece
        afib_pieces.append(afib_resampled[start:end])
        # create the annotations array for the 30 second piece
        ann_piece = []
        has_afib = (start_ann == '(AFIB')
        has_other = (start_ann != '(AFIB' and start_ann != '(N')
        if start_ann != None:
            ann_piece.append([0, start_ann])
        for i in range(0, ann.__dict__['ann_len']):
            ann_symbol = ann.__dict__['aux_note'][i]
            if start <= ann_samples[i] and ann_samples[i] < end:
                ann_piece.append([
                    ann_samples[i] - start,
                    ann_symbol])
                # find pieces with afib anns
                if ann_symbol == '(AFIB':
                    has_afib = True
                # find pieces with other anns
                elif ann_symbol != '(AFIB' and ann_symbol != '(N':
                    has_other = True
                start_ann = ann_symbol
        # identify afib pieces
        piece_index = len(afib_ann_pieces)
        # identify afib pieces
        if has_afib:
            # identify afib and other pieces
            if has_other:
                afib_afib_and_other_pieces.append(piece_index)
            # identify just afib pieces
            else:
                afib_afib_pieces.append(piece_index)
        # identify no afib pieces
        else:
            # identify other arrhythmia pieces
            if has_other:
                afib_other_pieces.append(piece_index)
            # identify normal pieces
            else:
                afib_normal_pieces.append(piece_index)
        afib_ann_pieces.append(ann_piece)
        start = end
        end += num_samps
        
print('Loaded',len(afib_pieces),'arrhythmia pieces')
print('Loaded',len(afib_ann_pieces),'arrhythmia annotations')
print('Found',len(afib_afib_pieces),'afib pieces')
print('Found',len(afib_afib_and_other_pieces),'afib and other pieces')
print('Found',len(afib_other_pieces),'pieces with other arrhythmia')
print('Found',len(afib_normal_pieces),'normal pieces')

