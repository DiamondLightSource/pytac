function load_unitconv(ringmode, renamedIndexes)
dir = fileparts(mfilename('fullpath'));
cd(dir);
units_file = fullfile(dir, '..', 'pytac', 'data', ringmode, 'unitconv.csv');
poly_file = fullfile(dir, '..', 'pytac', 'data', ringmode, 'uc_poly_data.csv');
pchip_file = fullfile(dir, '..', 'pytac', 'data', ringmode, 'uc_pchip_data.csv');

fprintf('Loading unit conversions...\n');

% These variables are used throughout this file.
f_units = fopen(units_file, 'w');
f_poly = fopen(poly_file, 'w');
f_pchip = fopen(pchip_file, 'w');
uc_id = 0;

fprintf(f_units, 'el_id,field,uc_type,uc_id,phys_units,eng_units\n');
fprintf(f_poly, 'uc_id,coeff,val\n');
fprintf(f_pchip, 'uc_id,eng,phy\n');

quad_families = findmemberof('QUAD');
sext_families = findmemberof('SEXT');

% Unit conversions for lattice fields
fprintf(f_units, '%d,%s,poly,%d,%s,%s\n', 0, 'energy', 0, 'Mev', 'Mev');
fprintf(f_poly, '%d,%d,%f\n', 0, 0, 0);
fprintf(f_poly, '%d,%d,%f\n', 0, 1, 1e-6);

% Lattice null unit conversions
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'm44', 0, '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 's_position', 0, 'm', 'm');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'alpha', 0, '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'beta', 0, 'm', 'm');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'mu', 0, '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'dispersion', 0, 'm', 'm');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'tune_x', 0, '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'tune_y', 0, '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'chromaticity_x', 0, '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'chromaticity_y', 0, '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'emittance_x', 0, 'nm', 'nm');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'emittance_y', 0, 'pm', 'pm');
fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 0, 'beam_current', 0, 'A', 'A');

% Element null unit conversions
s_data = getfamilydata('BBVMXS');
l_data = getfamilydata('BBVMXL');
db_indexes = [s_data.AT.ATIndex, l_data.AT.ATIndex];
db_indexes = db_indexes(:);
for i = 1:length(db_indexes)
    fprintf(f_units, '%d,%s,null,%d,%s,%s\n', renamedIndexes(db_indexes(i)), 'db0', 0, 'm^-1', 'A');
end
rfs = getfamilydata('RF');
if length(rfs.ElementList) > 1
    for i = 1:length(rfs.AT.ATIndex)
        fprintf(f_units, '%d,%s,null,%d,%s,%s\n', renamedIndexes(rfs.AT.ATIndex(i)), 'f', 0, 'Hz', 'Hz');
    end
else
    fprintf(f_units, '%d,%s,null,%d,%s,%s\n', 1490, 'f', 0, 'Hz', 'Hz');
end

for i = 1:length(quad_families)
    write_multipole_section(quad_families{i}, 'b1', renamedIndexes, 'm^-2', 'A');
end

for i = 1:length(sext_families)
    write_multipole_section(sext_families{i}, 'b2', renamedIndexes, 'm^-3', 'A');
end

bend_families = findmemberof('BEND');
for i = 1:length(bend_families)
    write_multipole_section(bend_families{i}, 'b0', renamedIndexes, 'm^-1', 'A');
end

bpms = getfamilydata('BPMx');
bpm_uc_id = write_linear_data(0.001, 0);
for i = 1:length(bpms.AT.ATIndex)
    fprintf(f_units, '%d,%s,poly,%d,%s,%s\n', renamedIndexes(bpms.AT.ATIndex(i)), 'x', bpm_uc_id, 'mm', 'm'); 
    fprintf(f_units, '%d,%s,poly,%d,%s,%s\n', renamedIndexes(bpms.AT.ATIndex(i)), 'y', bpm_uc_id, 'mm', 'm'); 
end

% The skew quadrupoles are windings on the sextupoles, but there is no
% separate element so this works correctly (see below).
write_multipole_section('SQUAD', 'a1', renamedIndexes, 'm^-2', 'A');

% If corrector magnets are windings on a sextupole, their AT Index is that
% of the sextupole whereas there is a separate element for those magnets.
% We have to use the index of the separate elements instead.
sext_data = getfamilydata('SEXT_');
sext_indices = sext_data.AT.ATIndex;

hcor = getfamilydata('HCM');
for i = 1:length(hcor.DeviceList)
    data = el_cal_data(hcor.Monitor.ChannelNames(i,:));
    hcor_index = hcor.AT.ATIndex(i);
    if any(hcor_index == sext_indices)
        hcor_index = hcor_index + 1;
    end
    id = write_linear_data(data.field(2) / data.current(2), 0);
    fprintf(f_units, '%d,%s,poly,%d,%s,%s\n', renamedIndexes(hcor_index), 'x_kick', id, 'rads^-2', 'A'); 
end

vcor = getfamilydata('VCM');
for i = 1:length(vcor.DeviceList)
    data = el_cal_data(vcor.Monitor.ChannelNames(i,:));
    vcor_index = vcor.AT.ATIndex(i);
    if any(vcor_index == sext_indices)
        vcor_index = vcor_index + 1;
    end
    id = write_linear_data(data.field(2) / data.current(2), 0);
    fprintf(f_units, '%d,%s,poly,%d,%s,%s\n', renamedIndexes(vcor_index), 'y_kick', id, 'rads^-2', 'A');
end


fclose(f_units);
fclose(f_poly);
fclose(f_pchip);

fprintf('Finished.\n');

    function id = write_linear_data(gradient, offset)
        uc_id = uc_id + 1; 
        fprintf(f_poly, '%d,%d,%f\n', uc_id, 0, offset);
        fprintf(f_poly, '%d,%d,%f\n', uc_id, 1, gradient);
        id = uc_id;
    end

    function id = write_pchip_data(hw, phy)
        uc_id = uc_id + 1;
        for i = 1:length(hw)
            fprintf(f_pchip, '%d,%0.8f,%0.8f\n', uc_id, hw(i), phy(i));
        end
        id = uc_id;
    end

    function write_multipole_section(family, field, renamedIndexes, phys_units, eng_units)
        % We need to get our own device list so we can set the StatusFlag to 0,
        % this returns devices which are currently disabled.
        device_list = family2dev(family, 0);
        a = hw2physics(family, 'Monitor', 100, device_list);
        if all(a / a(1) == 1)  % All the magnets in the family have the same

            % unit conversion.
            caldata = fam_cal_data(family);
            bpm_uc_id = write_pchip_data(caldata.current, caldata.field);
            fdata = getfamilydata(family);
            for j = 1:length(fdata.AT.ATIndex)
                fprintf(f_units, '%d,%s,pchip,%d,%s,%s\n', renamedIndexes(fdata.AT.ATIndex(j)), field, bpm_uc_id, phys_units, eng_units); 
            end
        else  % Need unit conversion data for each magnet in the family.
            irregular_mags = getfamilydata(family);
            for j = 1:length(irregular_mags.DeviceList)
                caldata = el_cal_data(irregular_mags.Monitor.ChannelNames(j,:));
                q_index = renamedIndexes(irregular_mags.AT.ATIndex(j));
                bpm_uc_id = write_pchip_data(caldata.current, caldata.field);
                fprintf(f_units, '%d,%s,pchip,%d,%s,%s\n', q_index, field, bpm_uc_id, phys_units, eng_units);        
            end
        end
    end

    function caldata = el_cal_data(channel_name)
        global calibration_data;
        index = calibration_lookup2(channel_name);
        caldata = calibration_data{index};
    end

    function caldata = fam_cal_data(famname)
        fd = getfamilydata(famname);
        chan = fd.Monitor.ChannelNames(1,:);
        caldata = el_cal_data(chan);
    end

end
