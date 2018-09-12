
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

fprintf(f_units, 'el_id,field,uc_type,uc_id\n');
fprintf(f_poly, 'uc_id,coeff,val\n');
fprintf(f_pchip, 'uc_id,eng,phy\n');

quad_families = findmemberof('QUAD');
sext_families = findmemberof('SEXT');

for i = 1:length(quad_families)
    write_multipole_section(quad_families{i}, 'b1');
end

for i = 1:length(sext_families)
    write_multipole_section(sext_families{i}, 'b2');
end

bend_families = findmemberof('BEND');
for i = 1:length(bend_families)
    write_multipole_section(bend_families{i},'b0');
end

bpms = getfamilydata('BPMx');
bpm_uc_id = write_linear_data(0.001, 0);
for i = 1:length(bpms.AT.ATIndex)
    fprintf(f_units, '%d,%s,poly,%d\n', renamedIndexes(bpms.AT.ATIndex(i)), 'x', bpm_uc_id); 
    fprintf(f_units, '%d,%s,poly,%d\n', renamedIndexes(bpms.AT.ATIndex(i)), 'y', bpm_uc_id); 
end

% The skew quadrupoles are windings on the sextupoles, but there is no
% separate element so this works correctly (see below).
write_multipole_section('SQUAD', 'a1', renamedIndexes);

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
    fprintf(f_units, '%d,%s,poly,%d\n', renamedIndexes(hcor_index), 'x_kick', id); 
end

vcor = getfamilydata('VCM');
for i = 1:length(vcor.DeviceList)
    data = el_cal_data(vcor.Monitor.ChannelNames(i,:));
    vcor_index = vcor.AT.ATIndex(i);
    if any(vcor_index == sext_indices)
        vcor_index = vcor_index + 1;
    end
    id = write_linear_data(data.field(2) / data.current(2), 0);
    fprintf(f_units, '%d,%s,poly,%d\n', renamedIndexes(vcor_index), 'y_kick', id);
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

    function write_multipole_section(family, field, units)
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
                fprintf(f_units, '%d,%s,pchip,%d\n', renamedIndexes(fdata.AT.ATIndex(j)), field, bpm_uc_id); 
            end
        else  % Need unit conversion data for each magnet in the family.
            irregular_mags = getfamilydata(family);
            for j = 1:length(irregular_mags.DeviceList)
                caldata = el_cal_data(irregular_mags.Monitor.ChannelNames(j,:));
                q_index = renamedIndexes(irregular_mags.AT.ATIndex(j));
                bpm_uc_id = write_pchip_data(caldata.current, caldata.field);
                fprintf(f_units, '%d,%s,pchip,%d\n', q_index, field, bpm_uc_id);        
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
