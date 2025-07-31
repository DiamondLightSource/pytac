function load_mml(ringmode)
% Extract data from middlelayer and write it into the CSV files
% used by Pytac.
% Middlelayer does not have a reliable API so this script is brittle
% and frequently needs changing.
% 
%     fprintf('Loading data for ring mode %s\n', ringmode);
% 
%     loaded_ringmode = getfamilydata('OperationalMode');
% 
%     if ~strcmp(loaded_ringmode, ringmode)
%         fprintf('MML ring mode %s loaded, not %s\n', loaded_ringmode, ringmode);
%         fprintf('Script will exit.\n');
%         return;
%     end

    switch2sim;

    dir = fileparts(mfilename('fullpath'));
    cd(dir);
    datadir = fullfile(dir, '..', ringmode);
    if ~exist(datadir, 'dir')
        fprintf('Data directory %s does not exist. Please create it.\n', datadir);
        fprintf('Script will exit.\n');
        return;
    end

    % Open the CSV files that store the Pytac data.
    elements_file = fullfile(datadir, 'elements.csv');
    f_elements = fopen(elements_file, 'wt', 'n', 'utf-8');
    fprintf(f_elements, 'type,length\n');
    epics_devices_file = fullfile(datadir, 'epics_devices.csv');
    f_epics_devices = fopen(epics_devices_file, 'w');
    fprintf(f_epics_devices, 'el_id,name,field,get_pv,set_pv\n');
    simple_devices_file = fullfile(datadir, 'simple_devices.csv');
    f_simple_devices = fopen(simple_devices_file, 'w');
    fprintf(f_simple_devices, 'el_id,field,value,readonly\n');
    families_file = fullfile(datadir, 'families.csv');
    f_families = fopen(families_file, 'w');
    fprintf(f_families, 'el_id,family\n');

    global THERING;
    ao = getao();

    % Get the beam energy value from the lattice.
    energy = THERING{1}.Energy;
    fprintf(f_simple_devices, '0,energy,%d,True\n', energy);

    % The individual BPM PVs are not stored in middlelayer.
    BPMS = get_bpm_pvs(ao);

    % Map from AT types to types in the accelerator object (ao).
    global TYPE_MAP;
    % Collective multiple and dipole arrays do not currently exist so use N/A
    % Multipole is currently just an alias for Octupole
    keys = {'Multipole', 'Quadrupole', 'Sextupole', 'VSTR', 'HSTR', 'Bend', 'VTRIM', 'HTRIM'};
    values = {'N/A', 'QUAD_', 'SEXT_', 'VCM', 'HCM', 'N/A', 'VTRIM', 'HTRIM'};
    TYPE_MAP = containers.Map(keys, values);

    used_elements = containers.Map();
    renamed_indexes = containers.Map('KeyType', 'int32', 'ValueType', 'int32');

    % These fields are not associated with an element as they are attached to
    % the lattice, we therefore must insert them separately at index 0.
    s = pv_struct('beam_current', 'SR-DI-DCCT-01:SIGNAL', '');
    insertpvs(0, {s});
    s = pv_struct('emittance_x', 'SR-DI-EMIT-01:HEMIT', '');
    insertpvs(0, {s});
    s = pv_struct('emittance_y', 'SR-DI-EMIT-01:VEMIT', '');
    insertpvs(0, {s});
    s = pv_struct('tune_x', 'SR23C-DI-TMBF-01:X:TUNE:TUNE', '');
    insertpvs(0, {s});
    s = pv_struct('tune_y', 'SR23C-DI-TMBF-01:Y:TUNE:TUNE', '');
    insertpvs(0, {s});

    new_index = 0;

    for old_index = 1:length(THERING)
        at_elem = THERING{old_index};
        % If an HSTR is preceded by a sext or a VSTR is two elements after
        % a sext, assume that they are in fact parts of the same element.
        % Just add that family to the sext element.
        % Don't increment the new_index count as we haven't added an
        % element.
        if (strcmp(at_elem.FamName, 'HSTR') && strcmp(THERING{old_index - 1}.Class, 'Sextupole')) || (strcmp(at_elem.FamName, 'VSTR') && strcmp(THERING{old_index - 2}.Class, 'Sextupole'))
            fprintf(f_families, '%i,%s\n', new_index, at_elem.FamName);
        else
            new_index = new_index + 1;
            insertelement(new_index, old_index, at_elem);
        end

        type = gettype(at_elem);
        if used_elements.isKey(type)
            used_elements(type) = used_elements(type) + 1;
        else
            used_elements(type) = 1;
        end
        pvs = getpvs(ao, at_elem);
        insertpvs(new_index, pvs);

        renamed_indexes(old_index) = new_index;
    end

    % The following families  and do not have their
    % own elements.  We insert their PVs separately.
    insertextrapvs('SQUAD', 'a1');
    insertextrapvs('BBVMXS', 'db0');
    insertextrapvs('BBVMXL', 'db0');

    renamed_indexes(old_index) = new_index;
    fclose(f_elements);
    fclose(f_epics_devices);
    fclose(f_simple_devices);
    fclose(f_families);

    fprintf('Loaded %d mml elements into %d pytac elements.\n', old_index, new_index);

    % finally, load unit conversion data
    load_unitconv(ringmode, renamed_indexes);

    function type = gettype(elem)
        if isfield(elem, 'Class')
            type = elem.Class;
            % We need to distinguish
            % - BPMs, which have class 'Marker'
            % - vertical and horizontal correctors
            if (strcmp(type, 'Marker') || strcmp(type, 'Corrector')) && isfield(elem, 'FamName')
                type = elem.FamName;
            end
        end
    end


    function insertpvs(index, pvs)
        if size(pvs) == 0
            return;
        end
        parts = strsplit(pvs{1}.get_pv,':');
        prefix = parts{1};
        for i = 1:size(pvs, 2)
            fprintf(f_epics_devices, '%d,%s,%s,%s,%s\n', index, prefix, pvs{i}.field, deblank(pvs{i}.get_pv), deblank(pvs{i}.set_pv));
        end
    end


    % Construct BPM PVs from MML indices
    function bpms = get_bpm_pvs(ao)
        nbpms = size(ao.BPMx.DeviceList, 1);
        bpms = cell(nbpms);
        for i = 1:nbpms
            ncell = ao.BPMx.DeviceList(i,1);
            index = ao.BPMx.DeviceList(i,2);
            if mod(ncell, 1) ~= 0
                % Indices of .5 correspond to SRnnS-DI-EBPM-nn.
                ncell = fix(ncell);
                bpms{i} = sprintf('SR%02dS-DI-EBPM-%02d', ncell, index);
            else
                bpms{i} = sprintf('SR%02dC-DI-EBPM-%02d', ncell, index);
            end
        end
    end


    function pvs = getpvs(ao, elem)
        type = gettype(elem);
        if any(ismember(type, TYPE_MAP.keys))

            index = used_elements(type);
            % MML is inconsistent about whether the family for the bends
            % is BEND or BB.
            if strcmp(type, 'Bend') && isfield(ao, 'Bend')
                family = 'BEND';
            else
                family = TYPE_MAP(type);
            end

            get_pv = char(ao.(family).Monitor.ChannelNames(index, :));
            set_pv = char(ao.(family).Setpoint.ChannelNames(index, :));
            alt_pv1 = {};
            alt_pv2 = {};

            if strcmp(type, 'Quadrupole')
                field = 'b1';
            elseif strcmp(type, 'Sextupole')
                field = 'b2';
            elseif strcmp(type, 'Bend')
                field = 'b0';
            elseif strcmp(type, 'VTRIM')
                field = 'y_kick';
            elseif strcmp(type, 'HTRIM')
                field = 'x_kick';
            elseif strcmp(type, 'VSTR')
                field = 'y_kick';
                alt_prefix = strrep(strrep(get_pv, 'DI', 'PC'), ':I', '');
                alt_template = strcat(alt_prefix, ':%s:DISABLED');
                alt_pv1 = pv_struct('v_fofb_disabled', sprintf(alt_template, 'FAST'), '');
                alt_pv2 = pv_struct('v_sofb_disabled', sprintf(alt_template, 'SLOW'), '');
            elseif strcmp(type, 'HSTR')
                field = 'x_kick';
                alt_prefix = strrep(strrep(get_pv, 'DI', 'PC'), ':I', '');
                alt_template = strcat(alt_prefix, ':%s:DISABLED');
                alt_pv1 = pv_struct('h_fofb_disabled', sprintf(alt_template,'FAST'), '');
                alt_pv2 = pv_struct('h_sofb_disabled', sprintf(alt_template, 'SLOW'), '');
            end
            pvs = pv_struct(field, get_pv, set_pv);
            if numel(alt_pv1) > 0 && numel(alt_pv2) > 0
                pvs = {pvs, alt_pv1, alt_pv2};
            else
                pvs = {pvs};
            end
        elseif strcmp(type, 'BPM')
            index = used_elements(type);
            enable_pv = strcat(BPMS{index}, ':CF:ENABLED_S');
            en_pv = pv_struct('enabled', enable_pv, '');
            get_x_pv = strcat(BPMS{index}, ':SA:X');
            x_pv = pv_struct('x', get_x_pv, '');
            get_y_pv = strcat(BPMS{index}, ':SA:Y');
            y_pv = pv_struct('y', get_y_pv, '');
            alt_prefix = strrep(strrep(BPMS{index}, 'DI', 'PC'), 'EBPM', '%sBPM');
            alt_template = strcat(alt_prefix, ':%s:DISABLED');
            x_fofb_pv = pv_struct('x_fofb_disabled', sprintf(alt_template, 'H', 'FAST'), '');
            x_sofb_pv = pv_struct('x_sofb_disabled', sprintf(alt_template, 'H', 'SLOW'), '');
            y_fofb_pv = pv_struct('y_fofb_disabled', sprintf(alt_template, 'V', 'FAST'), '');
            y_sofb_pv = pv_struct('y_sofb_disabled', sprintf(alt_template, 'V', 'SLOW'), '');
            pvs = {x_pv, y_pv, en_pv, x_fofb_pv, x_sofb_pv, y_fofb_pv, y_sofb_pv};
        elseif strcmp(type, 'RFCavity')
            gfpv = ao.('RF').Monitor.ChannelNames;
            sfpv = ao.('RF').Setpoint.ChannelNames;
            f_pvs = pv_struct('f', gfpv, sfpv);
            % voltage?
            pvs = {f_pvs};
        else
            pvs = {};
        end

    end

    function insertextrapvs(family, field)
        elems = getfamilydata(family);
        if ~isempty(elems)
            for i = 1:length(elems.AT.ATIndex)
                get_pv = elems.Monitor.ChannelNames(i,:);
                set_pv = elems.Setpoint.ChannelNames(i,:);
                pvs = pv_struct(field, get_pv, set_pv);
                insertpvs(renamed_indexes(elems.AT.ATIndex(i)), {pvs});
            end
        end
    end

    function s = pv_struct(field, get_pv, set_pv)
        s = struct('field', field, 'get_pv', get_pv, 'set_pv', set_pv);
    end

    function insertelement(i, old_i, at_elem)
        type = gettype(at_elem);
        fprintf(f_families, '%i,%s\n', i, at_elem.FamName);

        % Elements with additional PVs require an extra group added.
        % The ATIndex array lists the original indexes, so we need
        % old_index to correctly check if this element was a member
        % of the group.
        extra_groups = {'SQUAD'};
        for j = 1:length(extra_groups)
            group = extra_groups{j};
            elems = getfamilydata(group);
            if ~isempty(elems) && ismember(old_i, elems.AT.ATIndex)
                fprintf(f_families, '%i,%s\n', i, group);
            end
        end

        fprintf(f_elements, '%s,%f\n', type, at_elem.Length);
    end

end
