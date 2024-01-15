# arrhythmia ECG records

import wfdb

record_ids = [
    '100','101','102','103','104','105','106','107','108',
    '109','111','112','113','114','115','116','117','118',
    '119','121','122','123','124','200','201','202','203',
    '205','207','208','209','210','212','213','214','215',
    '217','219','220','221','222','223','228','230','231',
    '232','233','234']

# records = []
# for rec in record_ids:
#     record = wfdb.rdrecord(rec, pn_dir='mitdb')
#     records.append(record)

# to cut arrhythmia pieces
num_samps = 10800
arrhythmia_pieces = []
arrhythmia_ann_pieces = []
arrhythmia_afib_pieces = []
arrhythmia_normal_pieces = []
arrhythmia_other_pieces = []
arrhythmia_afib_and_other_pieces = []
arrhythmia_bad_pieces = 0

bad_ann = { 'qq\x00', 'U\x00', 'M\x00', 'MISSB\x00', 'P\x00', 'PE\x00', 'T\x00', 'TS\x00' }

for rec_id in record_ids:
    # read rec and ann
    rec = wfdb.rdrecord('mit-bih-arrhythmia-database-1.0.0/'+rec_id)
    ann = wfdb.rdann('mit-bih-arrhythmia-database-1.0.0/'+rec_id, extension='atr')
    start = 0
    end = num_samps
    start_ann = None
    while end <= 648000:
        # create the annotations array for the 30 second piece
        arrhythmia_ann_piece = []
        has_afib = (start_ann == '(AFIB')
        has_other = (start_ann not in bad_ann and start_ann != '(AFIB' and start_ann != '(N\x00')
        is_bad = (start_ann in bad_ann)
        if start_ann != None:
            arrhythmia_ann_piece.append([0, start_ann])
        for i in range(0, ann.__dict__['ann_len']):
            ann_symbol = ann.__dict__['aux_note'][i]
            if start <= ann.__dict__['sample'][i] and ann.__dict__['sample'][i] < end and ann_symbol != '':
                arrhythmia_ann_piece.append([
                    ann.__dict__['sample'][i] - start,
                    ann_symbol
                ])
                # find bad pieces
                if ann_symbol in bad_ann:
                    is_bad = True
                # find pieces with afib anns
                elif ann_symbol == '(AFIB':
                    has_afib = True
                # find pieces with other anns
                elif ann_symbol != '(AFIB' and ann_symbol != '(N\x00':
                    has_other = True
                start_ann = ann_symbol
        # identify afib pieces
        piece_index = len(arrhythmia_ann_pieces)
        # identify bad pieces
        if is_bad:
            arrhythmia_bad_pieces += 1
        else:
            # cut out the 30 second piece
            piece = rec.__dict__['p_signal'][start:end]
            if len(piece) == 0:
                print('hey, found a zero-length arrythmia piece with start =',start,', end =',end)
                start = end
                end += num_samps
                continue
            arrhythmia_pieces.append(piece)
            arrhythmia_ann_pieces.append(arrhythmia_ann_piece)
            # identify afib pieces
            if has_afib:
                # identify afib and other pieces
                if has_other:
                    arrhythmia_afib_and_other_pieces.append(piece_index)
                # identify just afib pieces
                else:
                    arrhythmia_afib_pieces.append(piece_index)
            # identify no afib pieces
            else:
                # identify other arrhythmia pieces
                if has_other:
                    arrhythmia_other_pieces.append(piece_index)
                # identify normal pieces
                else:
                    arrhythmia_normal_pieces.append(piece_index)
        start = end
        end += num_samps
        
print('FROM ARRHYTHMIA DB:')
print('Loaded',len(arrhythmia_pieces),'arrhythmia pieces')
print('Loaded',len(arrhythmia_ann_pieces),'arrhythmia annotations')
print('Found',len(arrhythmia_afib_pieces),'afib pieces')
print('Found',len(arrhythmia_afib_and_other_pieces),'afib and other pieces')
print('Found',len(arrhythmia_other_pieces),'pieces with other arrhythmia')
print('Found',len(arrhythmia_normal_pieces),'normal pieces')
print('Found',arrhythmia_bad_pieces,'bad pieces')

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
        piece = afib_resampled[start:end]
        if len(piece) == 0:
            print('hey, found a zero-length afib piece with start =',start,', end =',end)
            start = end
            end += num_samps
            continue
        afib_pieces.append(piece)
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

print('FROM AFIB DB:')        
print('Loaded',len(afib_pieces),'total afib pieces')
print('Loaded',len(afib_ann_pieces),'afib annotations')
print('Found',len(afib_afib_pieces),'afib pieces')
print('Found',len(afib_afib_and_other_pieces),'afib and other pieces')
print('Found',len(afib_other_pieces),'pieces with other arrhythmia')
print('Found',len(afib_normal_pieces),'normal pieces')

# combine 30s pieces from arrhythmia and afib databases
all_pieces = arrhythmia_pieces + afib_pieces
all_ann_pieces = arrhythmia_ann_pieces + afib_ann_pieces
all_afib_pieces = arrhythmia_afib_pieces + [i + len(arrhythmia_pieces) for i in afib_afib_pieces]
all_afib_and_other_pieces = arrhythmia_afib_and_other_pieces + [i + len(arrhythmia_pieces) for i in afib_afib_and_other_pieces]
all_other_pieces = arrhythmia_other_pieces + [i + len(arrhythmia_pieces) for i in afib_other_pieces]
all_normal_pieces = arrhythmia_normal_pieces + [i + len(arrhythmia_pieces) for i in afib_normal_pieces]

print('FROM BOTH AFIB DB and ARRHYTHMIA DB:')
print('Found',len(all_afib_pieces),'afib pieces')
print('Found',len(all_afib_and_other_pieces),'afib and other pieces')
print('Found',len(all_other_pieces),'other pieces')
print('Found',len(all_normal_pieces),'normal pieces')


# label all pieces: N = normal, A = afib, B = both afib and other, O = other
all_pieces_labels = ['N' for i in all_pieces]
for i in all_afib_pieces:
    all_pieces_labels[i] = 'A'
for i in all_afib_and_other_pieces:
    all_pieces_labels[i] = 'B'
for i in all_other_pieces:
    all_pieces_labels[i] = 'O'

# get target labels for output data (0 if not AFIB, 1 if AFIB)
all_pieces_targets = [1 if (l == 'A' or l == 'B') else 0 for l in all_pieces_labels]

print(len(all_pieces), 'remaining pieces')

print('Found',len([t for t in all_pieces_targets if t == 0]),'total not AFIB pieces')
print('Found',len([t for t in all_pieces_targets if t == 1]),'total AFIB pieces')