function load_unitconv(ringmode, renamedIndexes)
dir = fileparts(mfilename('fullpath'));
cd(dir);
datadir = fullfile(dir, '..', ringmode);
if ~exist(datadir, 'dir')
    fprintf('Data directory %s does not exist. Please create it.\n', datadir);
    fprintf('Script will exit.\n');
    return;
end

% Open the CSV files that store the Pytac data.
units_file = fullfile(datadir, 'unitconv.csv');
poly_file = fullfile(datadir, 'uc_poly_data.csv');
pchip_file = fullfile(datadir, 'uc_pchip_data.csv');

fprintf('Loading unit conversions...\n');

% These variables are used throughout this file.
f_units = fopen(units_file, 'w');
f_poly = fopen(poly_file, 'w');
f_pchip = fopen(pchip_file, 'w');
uc_id = 0;

% Add title rows.
fprintf(f_units, 'el_id,field,uc_type,uc_id,phys_units,eng_units,lower_lim,upper_lim\n');
fprintf(f_poly, 'uc_id,coeff,val\n');
fprintf(f_pchip, 'uc_id,eng,phy\n');


% Lattice null unit conversions
% lower and upper conversion limits are '' as NullUnitConvs do not convert
fprintf(f_units, '%d,%s,null,%d,%s,%s,%s,%s\n', 0, 's_position', uc_id, 'm', 'm', '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s,%s,%s\n', 0, 'beta', uc_id, 'm', 'm', '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s,%s,%s\n', 0, 'dispersion', uc_id, 'm', 'm', '', '');
fprintf(f_units, '%d,%s,null,%d,%s,%s,%s,%s\n', 0, 'beam_current', uc_id, 'A', 'A', '', '');

% Element null unit conversions
% lower and upper conversion limits are '' as NullUnitConvs do not convert
rfs = getfamilydata('RF');
if length(rfs.ElementList) == 1
    indexes = family2atindex('RF');
    for index = 1:length(indexes)
        fprintf(f_units, '%d,%s,null,%d,%s,%s,%s,%s\n', renamedIndexes(indexes(index)), 'f', 0, 'Hz', 'Hz', '', '');
    end
else
    for i = 1:length(rfs.AT.ATIndex)
        fprintf(f_units, '%d,%s,null,%d,%s,%s,%s,%s\n', renamedIndexes(rfs.AT.ATIndex(i)), 'f', 0, 'Hz', 'Hz', '', '');
    end
end

% Unit conversions for lattice fields
% the conversion limits are '' as these fields don't have a Setpoint field
uc_id = uc_id + 1;
fprintf(f_units, '%d,%s,poly,%d,%s,%s,%s,%s\n', 0, 'energy', uc_id, 'eV', 'MeV', '', '');
fprintf(f_poly, '%d,%d,%f\n', uc_id, 0, 0);
fprintf(f_poly, '%d,%d,%g\n', uc_id, 1, 1e6);
uc_id = uc_id + 1;
fprintf(f_units, '%d,%s,poly,%d,%s,%s,%s,%s\n', 0, 'emittance_x', uc_id, 'm', 'nm', '', '');
fprintf(f_poly, '%d,%d,%f\n', uc_id, 0, 0);
fprintf(f_poly, '%d,%d,%g\n', uc_id, 1, 1e-9);
uc_id = uc_id + 1;
fprintf(f_units, '%d,%s,poly,%d,%s,%s,%s,%s\n', 0, 'emittance_y', uc_id, 'm', 'pm', '', '');
fprintf(f_poly, '%d,%d,%f\n', uc_id, 0, 0);
fprintf(f_poly, '%d,%d,%g\n', uc_id, 1, 1e-12);

% Unit conversions for element fields
quad_families = findmemberof('QUAD');
for i = 1:length(quad_families)
    write_multipole_section(quad_families{i}, 'b1', renamedIndexes, 'm^-2', 'A');
end

sext_families = findmemberof('SEXT');
for i = 1:length(sext_families)
    write_multipole_section(sext_families{i}, 'b2', renamedIndexes, 'm^-3', 'A');
end

oct_families = [findmemberof('O0X'), findmemberof('O1X')];
for i = 1:length(oct_families)
    if ~isempty(oct_families{i})
        write_multipole_section(oct_families{i}, 'b3', renamedIndexes, 'm^-4', 'A');
    end
end

bend_families = findmemberof('BEND');
for i = 1:length(bend_families)
    if strcmp(bend_families{i}, 'BBVMXS') || strcmp(bend_families{i}, 'BBVMXL')
        % Double bend families
        write_multipole_section(bend_families{i}, 'db0', renamedIndexes, 'm^-1', 'A');
    else
        write_multipole_section(bend_families{i}, 'b0', renamedIndexes, 'm^-1', 'A');
    end
end

bpms = getfamilydata('BPMx');
bpm_uc_id = write_linear_data(0.001, 0);
% the conversion limits are '' as these fields don't have a Setpoint field
for i = 1:length(bpms.AT.ATIndex)
    fprintf(f_units, '%d,%s,poly,%d,%s,%s,%s,%s\n', renamedIndexes(bpms.AT.ATIndex(i)), 'x', bpm_uc_id, 'mm', 'm', '', '');
    fprintf(f_units, '%d,%s,poly,%d,%s,%s,%s,%s\n', renamedIndexes(bpms.AT.ATIndex(i)), 'y', bpm_uc_id, 'mm', 'm', '', '');
end

htrim = getfamilydata('HTRIM');
control_ranges = get_range('HTRIM');
for i = 1:length(htrim.AT.ATIndex)
    data = el_cal_data(htrim.Monitor.ChannelNames(i,:));
    id = write_linear_data(data.field(2) / data.current(2), 0);
    fprintf(f_units, '%d,%s,poly,%d,%s,%s,%d,%d\n', renamedIndexes(htrim.AT.ATIndex(i)), 'x_kick', id, '', 'A', control_ranges(i,1), control_ranges(i,2));
end

vtrim = getfamilydata('VTRIM');
control_ranges = get_range('VTRIM');
for i = 1:length(vtrim.AT.ATIndex)
    data = el_cal_data(vtrim.Monitor.ChannelNames(i,:));
    id = write_linear_data(data.field(2) / data.current(2), 0);
    fprintf(f_units, '%d,%s,poly,%d,%s,%s,%d,%d\n', renamedIndexes(vtrim.AT.ATIndex(i)), 'x_kick', id, '', 'A', control_ranges(i,1), control_ranges(i,2));
end

% The skew quadrupoles are windings on the sextupoles, but there is no
% separate element so this works correctly (see below).
% TODO: Still true for D2? Any SQUADS on octupoles?
write_multipole_section('SQUAD', 'a1', renamedIndexes, 'm^-2', 'A');

% If corrector magnets are windings on a sextupole or octupole, their AT Index is that
% of the sextupole or octupole. If they are independent, there is a separate element for
% the corrector magnets and we use the index of the separate element instead.
sext_data = getfamilydata('SEXT_');
sext_indices = sext_data.AT.ATIndex;
o0x_data = getfamilydata('O0X');
o1x_data = getfamilydata('O1X');

if ~isempty(o0x_data)
    oct_indices = o0x_data.AT.ATIndex;
else
    oct_indices = uint8.empty;
end

if ~isempty(o1x_data)
    oct_indices = cat(1, oct_indices, o1x_data.AT.ATIndex);
end

hcor = getfamilydata('HCM');
control_ranges = get_range('HCM');
for i = 1:length(hcor.AT.ATIndex)
    data = el_cal_data(hcor.Monitor.ChannelNames(i,:));
    hcor_index = hcor.AT.ATIndex(i);
    if any(hcor_index == sext_indices)
        hcor_index = hcor_index + 1;
    elseif any(hcor_index == oct_indices)
        hcor_index = hcor_index + 1;
    end
    id = write_linear_data(data.field(2) / data.current(2), 0);
    fprintf(f_units, '%d,%s,poly,%d,%s,%s,%d,%d\n', renamedIndexes(hcor_index), 'x_kick', id, '', 'A', control_ranges(i,1), control_ranges(i,2));
end

vcor = getfamilydata('VCM');
control_ranges = get_range('HCM');
for i = 1:length(vcor.AT.ATIndex)
    data = el_cal_data(vcor.Monitor.ChannelNames(i,:));
    vcor_index = vcor.AT.ATIndex(i);
    if any(vcor_index == sext_indices)
        vcor_index = vcor_index + 1;
    elseif any(vcor_index == oct_indices)
        vcor_index = vcor_index + 1;
    end
    id = write_linear_data(data.field(2) / data.current(2), 0);
    fprintf(f_units, '%d,%s,poly,%d,%s,%s,%d,%d\n', renamedIndexes(vcor_index), 'y_kick', id, '', 'A', control_ranges(i,1), control_ranges(i,2));
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
            control_ranges = get_range(family);
            for j = 1:length(fdata.AT.ATIndex)
                fprintf(f_units, '%d,%s,pchip,%d,%s,%s,%d,%d\n', renamedIndexes(fdata.AT.ATIndex(j)), field, bpm_uc_id, phys_units, eng_units, control_ranges(j,1), control_ranges(j,2));
            end
        else  % Need unit conversion data for each magnet in the family.
            irregular_mags = getfamilydata(family);
            control_ranges = get_range(family);
            for j = 1:length(irregular_mags.DeviceList)
                caldata = el_cal_data(irregular_mags.Monitor.ChannelNames(j,:));
                q_index = renamedIndexes(irregular_mags.AT.ATIndex(j));
                bpm_uc_id = write_pchip_data(caldata.current, caldata.field);
                fprintf(f_units, '%d,%s,pchip,%d,%s,%s,%d,%d\n', q_index, field, bpm_uc_id, phys_units, eng_units, control_ranges(j,1), control_ranges(j,2));
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

    function sp_range = get_range(famname)
        fd = getfamilydata(famname);
        if length(fd.Setpoint.Range(:,1)) == length(fd.AT.ATIndex)
            sp_range = fd.Setpoint.Range;
        else
            r = fd.Setpoint.Range(1, 1:2);
            all_r = r;
            for i = 1:length(fd.AT.ATIndex)-1
                all_r = [all_r; r];
            end
            sp_range = all_r;
        end
    end

end
